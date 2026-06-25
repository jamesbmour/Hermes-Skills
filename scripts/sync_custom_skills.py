#!/usr/bin/env python3
"""Sync Hermes skill directories between ~/.hermes/skills and this repo.

Safe defaults:
- No deletes are performed.
- Existing destination skills are not overwritten unless --all is provided.
- Pull/push skip skills whose `name:` already exists at another path unless --all is used.
- Internal Hermes cache directories (.hub, .trash, .usage.json) are ignored.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Tuple

EXCLUDE_NAMES = {
    ".git",
    ".hub",
    ".trash",
    ".usage.json",
    ".DS_Store",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}


@dataclass(frozen=True)
class SkillInfo:
    rel: str
    path: Path
    name: str
    digest: str


def hermes_home() -> Path:
    return Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes")).expanduser()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def parse_skill_name(skill_dir: Path) -> str:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="replace")[:5000]
    m = re.search(r"^name:\s*[\"']?([^\"'\n#]+)", text, flags=re.MULTILINE)
    return m.group(1).strip() if m else skill_dir.name


def iter_files(skill_dir: Path) -> Iterable[Path]:
    for p in sorted(skill_dir.rglob("*")):
        rel_parts = p.relative_to(skill_dir).parts
        if any(part in EXCLUDE_NAMES for part in rel_parts):
            continue
        if p.is_file() and not p.is_symlink():
            yield p


def content_hash(skill_dir: Path) -> str:
    h = hashlib.sha256()
    for p in iter_files(skill_dir):
        rel = p.relative_to(skill_dir).as_posix()
        h.update(rel.encode("utf-8"))
        h.update(b"\0")
        h.update(p.read_bytes())
        h.update(b"\0")
    return h.hexdigest()[:16]


def discover_skills(root: Path) -> Dict[str, SkillInfo]:
    """Return {relative_skill_dir: SkillInfo} for every SKILL.md under root."""
    out: Dict[str, SkillInfo] = {}
    if not root.exists():
        return out
    for skill_md in root.rglob("SKILL.md"):
        rel_parts = skill_md.relative_to(root).parts
        if any(part in EXCLUDE_NAMES for part in rel_parts):
            continue
        skill_dir = skill_md.parent
        rel = skill_dir.relative_to(root).as_posix()
        out[rel] = SkillInfo(rel=rel, path=skill_dir, name=parse_skill_name(skill_dir), digest=content_hash(skill_dir))
    return dict(sorted(out.items()))


def by_name(skills: Dict[str, SkillInfo]) -> Dict[str, list[SkillInfo]]:
    out: Dict[str, list[SkillInfo]] = {}
    for info in skills.values():
        out.setdefault(info.name, []).append(info)
    return out


def copy_skill(src: Path, dst: Path, overwrite: bool) -> str:
    if dst.exists():
        if not overwrite:
            return "skipped-existing"
        if dst.is_symlink() or dst.is_file():
            dst.unlink()
        else:
            shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns(*EXCLUDE_NAMES))
    return "copied"


def summarize(local_root: Path, repo: Path) -> Tuple[Dict[str, SkillInfo], Dict[str, SkillInfo]]:
    local = discover_skills(local_root)
    remote = discover_skills(repo)
    local_names = by_name(local)
    remote_names = by_name(remote)

    local_only_names = sorted(set(local_names) - set(remote_names))
    repo_only_names = sorted(set(remote_names) - set(local_names))
    path_only_repo = sorted(rel for rel, info in remote.items() if rel not in local and info.name in local_names)
    changed_same_path = sorted(rel for rel in set(local) & set(remote) if local[rel].digest != remote[rel].digest)

    print(f"Local skills root: {local_root}")
    print(f"Repo root:         {repo}")
    print(f"Local skill dirs:  {len(local)} ({len(local_names)} unique names)")
    print(f"Repo skill dirs:   {len(remote)} ({len(remote_names)} unique names)")

    print(f"Local-only names:  {len(local_only_names)}")
    for name in local_only_names:
        for info in local_names[name]:
            print(f"  + local  {info.rel}  (name: {name})")

    print(f"Repo-only names:   {len(repo_only_names)}")
    for name in repo_only_names:
        for info in remote_names[name]:
            print(f"  + repo   {info.rel}  (name: {name})")

    print(f"Repo-only paths whose skill name already exists locally: {len(path_only_repo)}")
    for rel in path_only_repo:
        info = remote[rel]
        local_rels = ", ".join(i.rel for i in local_names[info.name])
        print(f"  = repo   {rel}  (name: {info.name}; local at {local_rels})")

    print(f"Changed same-path skills: {len(changed_same_path)}")
    for rel in changed_same_path:
        print(f"  * diff   {rel}  (name: {local[rel].name})")
    return local, remote


def run_git(repo: Path, args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args], cwd=repo, text=True, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, check=check,
    )


def maybe_commit_and_push(repo: Path, do_commit: bool, do_push: bool) -> None:
    if do_commit:
        run_git(repo, ["add", "."])
        status = run_git(repo, ["status", "--porcelain"]).stdout.strip()
        if not status:
            print("No repo changes to commit.")
        else:
            msg = "sync: update Hermes custom skills"
            # Desktop/TUI sessions may not have James's 1Password SSH/GPG agent
            # socket, so make the automation commit unsigned. Normal manual git
            # workflows can still use the user's global signing config.
            print(run_git(repo, ["-c", "commit.gpgsign=false", "commit", "-m", msg]).stdout.rstrip())
    if do_push:
        print(run_git(repo, ["push"]).stdout.rstrip())


def do_pull(local_root: Path, repo: Path, overwrite: bool) -> None:
    remote = discover_skills(repo)
    local = discover_skills(local_root)
    local_names = by_name(local)
    copied = skipped = 0
    for rel, src in remote.items():
        dst = local_root / rel
        if rel in local and src.digest == local[rel].digest:
            skipped += 1
            continue
        if not overwrite and src.name in local_names and rel not in local:
            skipped += 1
            print(f"skipped {rel} (already have skill name '{src.name}')")
            continue
        result = copy_skill(src.path, dst, overwrite=overwrite)
        if result == "copied":
            copied += 1
            print(f"pulled {rel}")
        else:
            skipped += 1
    print(f"Pull complete: copied={copied}, skipped={skipped}, overwrite={overwrite}")


def do_push(local_root: Path, repo: Path, overwrite: bool, commit: bool, push: bool) -> None:
    local = discover_skills(local_root)
    remote = discover_skills(repo)
    remote_names = by_name(remote)
    copied = skipped = 0
    for rel, src in local.items():
        dst = repo / rel
        if rel in remote and src.digest == remote[rel].digest:
            skipped += 1
            continue
        if not overwrite and src.name in remote_names and rel not in remote:
            skipped += 1
            existing = ", ".join(i.rel for i in remote_names[src.name])
            print(f"skipped {rel} (repo already has skill name '{src.name}' at {existing})")
            continue
        result = copy_skill(src.path, dst, overwrite=overwrite)
        if result == "copied":
            copied += 1
            print(f"pushed {rel}")
        else:
            skipped += 1
    print(f"Push copy complete: copied={copied}, skipped={skipped}, overwrite={overwrite}")
    maybe_commit_and_push(repo, commit, push)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync Hermes custom skills with this Git repo.")
    parser.add_argument("command", choices=["status", "pull", "push", "sync"], nargs="?", default="status")
    parser.add_argument("--all", action="store_true", help="Overwrite changed existing skills. Without this, only missing skill names are copied.")
    parser.add_argument("--commit", action="store_true", help="Commit repo changes after push/sync.")
    parser.add_argument("--push", action="store_true", help="git push after committing or copying changes.")
    parser.add_argument("--skills-root", type=Path, default=hermes_home() / "skills")
    parser.add_argument("--repo-root", type=Path, default=repo_root())
    args = parser.parse_args(argv)

    local_root = args.skills_root.expanduser().resolve()
    repo = args.repo_root.expanduser().resolve()
    overwrite = bool(args.all)

    if args.command == "status":
        summarize(local_root, repo)
    elif args.command == "pull":
        run_git(repo, ["pull", "--ff-only"], check=False)
        do_pull(local_root, repo, overwrite=overwrite)
    elif args.command == "push":
        do_push(local_root, repo, overwrite=overwrite, commit=args.commit, push=args.push)
    elif args.command == "sync":
        run_git(repo, ["pull", "--ff-only"], check=False)
        do_pull(local_root, repo, overwrite=False)
        do_push(local_root, repo, overwrite=overwrite, commit=args.commit, push=args.push)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
