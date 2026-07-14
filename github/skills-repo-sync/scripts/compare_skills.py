#!/usr/bin/env python3
"""Compare live skills dir to repo, print diff categories.
Usage: python3 compare_skills.py [LIVE_DIR] [REPO_DIR]
Defaults: ~/.hermes/skills/ and ~/.hermes/home/Hermes-Skills/
"""
import os, hashlib, sys

LIVE = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/.hermes/skills")
REPO = sys.argv[2] if len(sys.argv) > 2 else os.path.expanduser("~/.hermes/home/Hermes-Skills")

# Files/dirs to skip (internal Hermes state, bundled symlinks)
SKIP = {
    ".bundled_manifest", ".curator_backups", ".curator_state",
    ".hub", ".usage.json", ".usage.json.lock", ".agents",
    "find-skills", "frontend-design", "web-design-guidelines",
    "SYNC_TEST.md", "Dev,Web", "__pycache__",
}

def scan(root):
    results = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        if ".git" in dirpath:
            continue
        dirnames[:] = [d for d in dirnames if d != ".git"]
        for f in filenames:
            abs_path = os.path.join(dirpath, f)
            rel = os.path.relpath(abs_path, root)
            # Check skip patterns
            parts = rel.split(os.sep)
            if any(p in SKIP for p in parts) or rel in SKIP:
                continue
            try:
                with open(abs_path, "rb") as fh:
                    h = hashlib.sha256(fh.read()).hexdigest()[:12]
                results[rel] = h
            except (PermissionError, OSError):
                pass
    return results

live = scan(LIVE)
repo = scan(REPO)

only_live = sorted(set(live) - set(repo))
only_repo = sorted(set(repo) - set(live))
both = sorted(set(live) & set(repo))
modified = [r for r in both if live[r] != repo[r]]

print(f"Live: {len(live)} files, Repo: {len(repo)} files")
print(f"\n=== NEW (only in live): {len(only_live)} ===")
for r in only_live:
    print(f"  + {r}")
print(f"\n=== DELETED (only in repo): {len(only_repo)} ===")
for r in only_repo:
    print(f"  - {r}")
print(f"\n=== MODIFIED: {len(modified)} ===")
for r in modified:
    print(f"  ~ {r}  live={live[r]} repo={repo[r]}")
print(f"\n=== UNCHANGED: {len(both) - len(modified)} ===")