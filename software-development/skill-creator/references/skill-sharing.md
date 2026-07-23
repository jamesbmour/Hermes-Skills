# Sharing & Exporting Skills Between Hermes Installs

How to transfer a locally-created skill from one Hermes installation to another.
Distilled from a live session working through every available mechanism.

## Mechanisms (best to simplest)

### 1. `hermes skills publish` → `hermes skills install` (best for sharing widely)

Publish to a GitHub repo, then anyone can install with a one-liner.

```bash
# On the source machine:
hermes skills publish ~/.hermes/skills/equity-research --to github --repo your-username/your-skills-repo

# On the receiving machine:
hermes skills install your-username/your-skills-repo/equity-research
```

This is the most robust path — it goes through the security scanner and
tracks provenance as a hub skill, so the receiver gets updates.

### 2. `hermes skills install` from a local directory

Copy the skill directory to the receiving machine (scp, AirDrop, USB),
then install through the proper pipeline:

```bash
hermes skills install /path/to/copied/equity-research --name equity-research --force --yes
```

- Runs a security scan before installing.
- `--force` is needed if a skill with that name already exists.
- `--name` overrides the name (useful if frontmatter name collides).
- Install from a bare `SKILL.md` file path does NOT work — must be a directory.

### 3. Tarball (simplest, no CLI needed)

```bash
# Source machine:
tar czf equity-research-skill.tar.gz -C ~/.hermes/skills equity-research

# Receiving machine:
tar xzf equity-research-skill.tar.gz -C ~/.hermes/skills/
```

No security scan, no provenance tracking, but works anywhere.
The skill is active on the next session — no restart needed.

### 4. Raw file copy (single-file skills only)

If the skill is just a `SKILL.md` with no linked files/scripts, copy
the file directly:

```bash
# On the receiving machine:
mkdir -p ~/.hermes/skills/equity-research
scp source:~/.hermes/skills/equity-research/SKILL.md ~/.hermes/skills/equity-research/
```

## What does NOT work

- **`hermes skills snapshot export`** — only captures hub-installed skills,
  not locally-created ones. Exporting a local skill produces an empty
  `"skills": []` array. Do not rely on snapshot for local skill transfer.

- **`hermes skills install <SKILL.md file path>`** — installing from a
  bare file path (not a directory) fails with "Could not fetch from any
  source." Must pass the skill's parent directory.

- **`file://` URLs** — `hermes skills install file:///path/to/SKILL.md`
  also fails. The installer only supports `https://` URLs and local
  directory paths.

## Pitfall: `hermes skills publish` may fail with "GitHub token lacks permission to fork repos"

Even with `repo` scope on the GitHub token, `hermes skills publish --to github`
can fail. The publish command tries to fork or create a repo through the API
in a way that requires permissions beyond standard `repo` scope.

**Workaround — manual gh CLI push:**

```bash
# 1. Create the repo
gh repo create your-username/Hermes-Skills --public --description "Hermes Agent skills"

# 2. Clone, copy skill directories, push
gh repo clone your-username/Hermes-Skills /tmp/Hermes-Skills
cd /tmp/Hermes-Skills
cp -R ~/.hermes/skills/equity-research equity-research
git add -A && git commit -m "Add equity-research skill" && git push origin main

# 3. Install on any Hermes machine
hermes skills install your-username/Hermes-Skills/equity-research
```

This produces the same result as `hermes skills publish` — the skill is
installable via `hermes skills install <owner>/<repo>/<skill-name>` —
but bypasses the permission issue.

## Pitfall: Local skills may be symlinks to `~/.agents/skills/`

Some local skills are symlinks pointing to `~/.agents/skills/<name>`. When
copying skill directories to a repo or tarball, resolve the real path first
or use `cp -L` (follow symlinks) instead of `cp -R`:

```bash
# Check if a skill is a symlink
ls -la ~/.hermes/skills/find-skills

# If symlink, copy the resolved target
cp -R ~/.agents/skills/find-skills /tmp/Hermes-Skills/find-skills

# Or use -L to follow symlinks
cp -RL ~/.hermes/skills/find-skills /tmp/Hermes-Skills/find-skills
```

Using `cp -R` on a symlink copies the symlink itself, not the contents —
git then stages it as a symlink object, which won't work on the receiving
machine if the target path doesn't exist there.

## Setting Up Ongoing Bidirectional Sync with GitHub

For keeping skills in sync between a local Hermes install and a GitHub
repo on an ongoing basis (e.g. nightly), use a shell script + cron job
pattern. This is the automated, recurring version of the transfer
methods above.

### The sync script

Create at `~/.hermes/scripts/sync-skills-to-github.sh`:

```bash
#!/bin/bash
set -euo pipefail

# Resolve the real Hermes home — $HOME may be overridden in some
# environments (e.g. Hermes WebUI sets $HOME to ~/.hermes/home).
# Fall back to getent passwd to find the actual user home.
if [ -n "${HERMES_HOME:-}" ]; then
  SKILLS_DIR="$HERMES_HOME/skills"
else
  REAL_HOME=$(getent passwd "$(whoami)" | cut -d: -f6)
  if [ -d "$REAL_HOME/.hermes/skills" ]; then
    SKILLS_DIR="$REAL_HOME/.hermes/skills"
  else
    SKILLS_DIR="$HOME/.hermes/skills"
  fi
fi

REPO_DIR="$HOME/Hermes-Skills"

# Exclude symlinked skills (managed separately) and metadata files
SYMLINKS=("equity-research" "find-skills" "skill-creator" "us-stock-researcher")
META=(".bundled_manifest" ".usage.json" ".usage.json.lock" ".curator_state" ".curator_backups" ".hub" "__pycache__")
EXCLUDE_ARGS=()
for item in "${SYMLINKS[@]}" "${META[@]}"; do EXCLUDE_ARGS+=(--exclude="$item"); done
EXCLUDE_ARGS+=(--exclude='.git')

cd "$REPO_DIR"
git pull origin main --ff-only 2>&1 || true
rsync -a --delete "${EXCLUDE_ARGS[@]}" "$SKILLS_DIR/" "$REPO_DIR/"
cd "$REPO_DIR"
if git diff --quiet && git diff --cached --quiet; then exit 0; fi
git add -A
git commit -m "sync: nightly skills sync — $(date -u +'%Y-%m-%d %H:%M UTC')" 2>&1
git push origin main 2>&1 || echo "WARNING: Push failed — check GitHub auth"
```

Key properties:
- **Silent on no changes** — exits 0 with empty stdout, so cron delivers nothing
- **Excludes symlinks** — symlinked skills point to `~/.agents/skills/` and are managed separately
- **Excludes metadata** — `.bundled_manifest`, `.usage.json`, `.curator_state`, etc. are environment-specific
- **Push failures are non-fatal** — warns but doesn't crash, so pull+rsync+commit still work without a token

### Cron job setup

Use the `cronjob` tool with `no_agent=true` (pure shell script, no LLM
needed per run — zero token cost):

```
cronjob(
  action='create',
  name='Nightly Skills Sync',
  schedule='0 3 * * *',
  no_agent=true,
  script='sync-skills-to-github.sh',
  deliver='origin'   # notifies chat only when script produces output (i.e. changes were pushed)
)
```

With `no_agent=true`, the script's stdout is delivered verbatim. Empty
stdout = silent (no notification). Non-zero exit = error alert.

### GitHub authentication for push

The sync script needs a GitHub PAT to push. Options:

1. **GITHUB_TOKEN in `.env`** — add `GITHUB_TOKEN=ghp_...` to `~/.hermes/.env`
2. **gh auth login** — install gh CLI and authenticate interactively
3. **Credential helper** — `git config --global credential.helper store` + `~/.git-credentials`

Without auth, the script still pulls (public repos) and commits locally,
but push will fail. The script handles this gracefully.

### Pitfall: $HOME override in Hermes WebUI

In Hermes WebUI environments, `$HOME` may be set to `~/.hermes/home`
rather than the real user home (e.g. `/home/hermeswebui`). This causes
`$HOME/.hermes/skills` to resolve to a nonexistent path. Always use
`getent passwd "$(whoami)"` or check `$HERMES_HOME` in scripts that
need to locate the Hermes skills directory.

### Pitfall: Overwriting skills not in the repo

When syncing from repo to local with rsync `--delete`, any local-only
skills (e.g. plugin-provided skills like `hermes-troubleshooting`) that
aren't in the repo will be deleted. To avoid this, either:
- Add them to the repo, or
- Add them to the SYMLINKS/exclude list in the sync script

The sync script above only syncs repo → local during the initial setup
(manual copy). The ongoing cron syncs local → repo (rsync source is
local, destination is repo), so local-only skills are pushed TO the
repo, not deleted from local.

## Determining skill complexity before transfer

Before choosing a transfer method, check whether the skill has linked
files (references, templates, scripts, assets):

```bash
find ~/.hermes/skills/<skill-name> -type f
```

- **Single-file skill** (only `SKILL.md`): any method works, including
  raw file copy.
- **Multi-file skill** (has `references/`, `scripts/`, etc.): use
  tarball or `hermes skills install <directory>` — a bare `SKILL.md`
  copy will miss the linked files and break the skill.