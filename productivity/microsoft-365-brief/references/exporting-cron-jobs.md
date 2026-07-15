# Exporting Cron Jobs to Another Hermes Install

When the user asks to export a cron job (or set of jobs) for import into another
Hermes system, follow this pattern.

## What to Export

For each job, capture:
- **Full prompt text** — not just the preview. Read from `~/.hermes/cron/jobs.json`
  (it's a dict with `jobs` key, each job has `id`, `name`, `prompt`, `schedule`,
  `model`, `provider`, `deliver`, `enabled_toolsets`, `no_agent`, `script`, etc.)
- **Script content** — if the job is `no_agent: true` with a `script` field, read
  the script from `~/.hermes/scripts/<script_name>`.
- **Job metadata** — schedule, model, provider, deliver target, toolsets, repeat.

## Export Bundle Structure

```
export-name/
├── README.md              # Prerequisites + import instructions
├── job-metadata.json      # Schedule, model, toolsets, delivery config
├── prompt.md              # Full prompt text (for LLM-driven jobs)
└── script.sh              # Script content (for script-only jobs)
```

Also create a top-level `.tar.gz` for easy download.

## README Must Include

1. **Prerequisites** — what the new install needs (skills, OAuth tokens, git
   repos, database files, API keys)
2. **Path updates** — every hardcoded path in the prompt/scripts that must be
   changed for the new system (MGAPI path, kanban.db path, HERMES_HOME, etc.)
3. **Import commands** — exact `hermes cron create` CLI commands or `cronjob`
   tool invocations with all parameters
4. **Verification steps** — how to confirm the job runs correctly after import

## Reading Full Job Definitions

The `cronjob` tool's `list` action only shows a `prompt_preview` (truncated).
To get the full prompt:

```python
import json
with open(f"{HERMES_HOME}/cron/jobs.json") as f:
    data = json.load(f)  # dict with 'jobs' key
for j in data['jobs']:
    if j['name'] == 'Target Job Name':
        print(j['prompt'])  # full untruncated prompt
```

Job IDs in `jobs.json` use `id` (not `job_id`); the cronjob tool uses `job_id`.

## Common Path Variables to Update

| Variable | Original (this install) | Portable equivalent |
|----------|-------------------------|---------------------|
| MGAPI script | `/home/hermeswebui/.hermes/skills/...` | `$HERMES_HOME/skills/...` or `~/.hermes/skills/...` |
| kanban.db | `/home/hermeswebui/.hermes/kanban.db` | `$HERMES_HOME/kanban.db` or `~/.hermes/kanban.db` |
| Scripts dir | `/home/hermeswebui/.hermes/scripts/` | `$HERMES_HOME/scripts/` or `~/.hermes/scripts/` |
| Backups dir | `/home/hermeswebui/.hermes/backups/` | `$HERMES_HOME/backups/` or `~/.hermes/backups/` |