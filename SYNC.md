# Hermes Skills Sync

This repo is configured as a local source for James's Hermes skills.

## One-time local setup

The local clone lives at:

```bash
~/.hermes/repos/Hermes-Skills
```

The Hermes skill tap is configured for this GitHub repo at the repository root.

## Commands

From this repo:

```bash
# See differences between ~/.hermes/skills and this repo
python3 scripts/sync_custom_skills.py status

# Pull repo skills into ~/.hermes/skills without overwriting existing local skills
python3 scripts/sync_custom_skills.py pull

# Push local-only skills into this repo without overwriting repo skills
python3 scripts/sync_custom_skills.py push

# Push local changes too, then commit and push to GitHub
python3 scripts/sync_custom_skills.py push --all --commit --push

# Safe two-way sync: pull missing repo skills, then push missing local skills
python3 scripts/sync_custom_skills.py sync --commit --push
```

There is also a convenience wrapper:

```bash
~/.hermes/scripts/sync-hermes-skills status
~/.hermes/scripts/sync-hermes-skills sync --commit --push
```

Safe defaults: no deletes, and no overwrites unless `--all` is passed.
