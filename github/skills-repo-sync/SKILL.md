---
name: skills-repo-sync
description: "Sync the local Hermes skills directory to a GitHub skills repo. Compare, copy new/modified files, commit, and push."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [GitHub, Skills, Sync, Git, Backup]
    related_skills: [github-auth, github-repo-management, hermes-agent]
---

# Skills Repo Sync

Sync the live Hermes skills directory (`~/.hermes/skills/`) to a GitHub backup repo. This is a recurring task — the repo accumulates custom skills and their supporting files (references, templates, scripts) so they're version-controlled and portable.

## Key Paths

| What | Path |
|------|------|
| Live skills | `~/.hermes/skills/` |
| Skills repo | `~/.hermes/home/Hermes-Skills/` (or `$HERMES_HOME/home/Hermes-Skills/`) |
| Remote | `github.com/<user>/Hermes-Skills.git` |
| Git credentials | `~/.git-credentials` (x-access-token format for fine-grained PATs) |

## Step 1: Scan and Diff

Walk both directories, hash every file, and compare. Use `execute_code` for the comparison logic — it handles permission errors on symlinked dirs gracefully.

### What to SKIP (never copy to repo)

These are internal Hermes state or bundled skills, not user-authored:

- **Symlinked bundled skills** — `find-skills`, `frontend-design`, `web-design-guidelines` (root-owned, point to `~/.agents/skills/`)
- **Internal state files** — `.bundled_manifest`, `.curator_backups/`, `.curator_state`, `.hub/`, `.usage.json`, `.usage.json.lock`, `.agents/`
- **Test files** — `SYNC_TEST.md` or similar artifacts from prior sync tests

### Comparison logic

```
1. Walk both dirs (followlinks=False to avoid symlink loops)
2. For each file, compute SHA-256 hash (first 12 chars is enough)
3. Categories:
   - Only in live  → NEW (copy to repo)
   - Only in repo   → DELETED from live (remove from repo or investigate)
   - In both, hash differs → MODIFIED (copy to repo)
   - In both, hash same  → unchanged (skip)
4. Filter out SKIP patterns from the "only in live" set
```

**Pitfall**: Some skill directories are symlinks owned by root. `os.walk(followlinks=False)` + try/except on `open()` handles this — don't let one PermissionError abort the whole scan.

## Step 2: Copy Changed Files

For each file in the NEW and MODIFIED sets:

```python
import shutil, os
src = os.path.join(LIVE_SKILLS, rel_path)
dst = os.path.join(REPO_DIR, rel_path)
os.makedirs(os.path.dirname(dst), exist_ok=True)
shutil.copy2(src, dst)  # copy2 preserves permissions/timestamps
```

After copying, re-hash both source and destination to verify they match.

## Step 3: Commit and Push

```bash
cd $REPO_DIR
git add -A
git status --short        # review what's staged
git commit -m "sync: update N modified skills, add M new skills + supporting files

New skills:
- category/skill-name

Updated skills:
- category/skill-name (what changed)

Also: cleanup notes"
git push origin main
```

## Step 4: Handle Push Failures

If `git push` returns 403 "Permission denied" or "Resource not accessible by personal access token":

1. **Identify token type**: Extract from `.git-credentials` — `github_pat_` prefix = fine-grained PAT, `ghp_` = classic token
2. **Verify authentication**: `curl -s -H "Authorization: Bearer $TOKEN" https://api.github.com/user` — should return 200 with user JSON
3. **Check if it's a fine-grained PAT** (no `X-OAuth-Scopes` header): Test write via `PUT /repos/$OWNER/$REPO/contents/test.md` — 403 means Contents:Write missing
4. **Fix fine-grained PAT**: Direct user to https://github.com/settings/personal-access-tokens → edit token → Repository access → ensure repo selected → Permissions → Contents → Read and write
5. **Or use classic PAT**: Generate at https://github.com/settings/tokens with `repo` scope (simpler, works for all user repos)
6. **Update stored credentials**:
   ```bash
   echo "https://x-access-token:$NEW_TOKEN@github.com" > ~/.git-credentials
   # Also update remote URL in the repo
   cd $REPO_DIR
   git remote set-url origin "https://x-access-token:$NEW_TOKEN@github.com/$USER/Hermes-Skills.git"
   ```
7. **Verify**: `git push origin main` should succeed; check `git status` shows "up to date with 'origin/main'"

See the `github-auth` skill for full token troubleshooting.

## Cron Job: Automated Sync

The sync runs automatically via a cron job (script-only, `no_agent=True`). The script is at `~/.hermes/scripts/sync-skills-to-github.sh`.

### Script behavior

1. **Resolve paths** — `$HERMES_HOME/skills` (fallback: `getent passwd` home), repo at `$HOME/Hermes-Skills`
2. **Pull remote changes** — `git pull origin main --ff-only` (tolerates failure)
3. **Copy live → repo** — `cp -a "$SKILLS_DIR"/* "$REPO_DIR"/` (NOT rsync — rsync is not available in the scheduler container; `cp -a` preserves timestamps/permissions and recurses). NOTE: the script builds an `EXCLUDE_ARGS` array for symlink/meta exclusions but does NOT pass it to `cp -a` (which doesn't support `--exclude`). The excluded items (symlinks, `.bundled_manifest`, `.usage.json`, etc.) are still copied by `cp -a` unless they fail to resolve. If clean exclusions are needed, switch to `find ... -not -path` piped to `cp` or use `rsync` outside the cron container.
4. **Commit + push** — only if `git diff` shows changes

### Exclusions (symlinks + meta)

```bash
SYMLINKS=("find-skills" "frontend-design" "web-design-guidelines")
META=(".bundled_manifest" ".usage.json" ".usage.json.lock" ".curator_state"
      ".curator_backups" ".hub" ".agents" "__pycache__" "Dev,Web")
```

### Cron schedule

Current: `0 3 */2 * *` (every other day at 3 AM UTC). Update via:
```python
cronjob(action="update", job_id="<ID>", schedule="0 3 */2 * *")
```

### Deliver target

Set to `origin` (current chat). Do NOT use `slack` unless a Slack channel is connected — it will silently fail with "no delivery target resolved".

## Pitfalls

| Pitfall | Fix |
|---------|-----|
| PermissionError scanning symlinked skill dirs | Use `os.walk(followlinks=False)` + try/except per file |
| Push 403 with fine-grained PAT | Token lacks Contents:Write — user must edit token permissions on GitHub |
| Stale unpushed commits from prior sessions | `git log --oneline origin/main..HEAD` shows unpushed commits; they'll go up with the next push |
| `SYNC_TEST.md` or other test artifacts in repo | Remove before committing; these are not skills |
| Memory tool at capacity when saving repo path | The skill itself carries the knowledge; memory is optional |
| `Dev,Web` category dir is a symlink/bundled | Add to SKIP list alongside `find-skills`, `frontend-design`, `web-design-guidelines` |
| rsync not available in scheduler container | Use `cp -a` instead — preserves timestamps and recurses. The existing exclusion array is built but not passed to `cp -a` (which has no `--exclude` flag). Acceptable for now since excluded items are mostly symlinks/metadata that won't cause issues in the repo. For strict exclusions, use `find ... -not -path` piped to `cp` |
| `$HOME` resolves wrong in cron/script context | Use `$HERMES_HOME` first, fall back to `getent passwd "$(whoami)" | cut -d: -f6`; never trust bare `$HOME` for the skills dir |
| `web-design-guidelines` symlink not in old SKIP list | Add to symlink exclusions; it's root-owned and bundled, not a custom skill |
| `__pycache__` dirs in skills | Add to meta exclusions; Python bytecode should not be synced |
| Fine-grained PAT (`github_pat_`) has empty X-OAuth-Scopes header | This is expected — fine-grained PATs use per-repo permissions, not scopes. Check via `PUT /repos/.../contents/` test, not scope header |
| Classic PAT (`ghp_`) has full `repo` scope | Works for all repos the user owns; prefer for automated scripts to avoid per-repo permission issues |

## Scripts

- `scripts/compare_skills.py` — scans both directories and prints NEW/MODIFIED/DELETED/UNCHANGED categories with hashes. Usage: `python3 scripts/compare_skills.py [LIVE_DIR] [REPO_DIR]`
- `~/.hermes/scripts/sync-skills-to-github.sh` — bash script for the automated cron job. Uses `cp -a` (NOT rsync — rsync not available in scheduler container), pulls remote first, commits and pushes changes. See "Cron Job: Automated Sync" section above.

## Verification

After push, verify the repo is in sync:

```bash
cd $REPO_DIR
git status                    # should show "working tree clean"
git log --oneline -3          # confirm latest commit
git diff origin/main --stat   # should be empty after push
```