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