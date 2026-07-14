# Cron / Container Environment-Mismatch Debugging

A script works when run manually from the terminal but fails when Hermes cron executes it. The symptom is often a missing file or wrong path even though the file exists on the host.

## Root cause

Hermes cron scripts run inside a container/namespaced environment. The scheduler sets `HERMES_HOME` to the in-container path (e.g. `/home/hermes/.hermes`), which may differ from the host path (e.g. `/home/hermeswebui/.hermes`). Scripts that hardcode host paths or rely on `~` resolving to the host home will fail.

## Diagnostic recipe

1. Check the live cron output file in `HERMES_HOME/cron/output/{job_id}/` for the exact script stderr.
2. Compare:
   - Manual run: `HERMES_HOME=/home/hermeswebui/.hermes bash /path/to/script.sh`
   - Cron run: inspect the output file for `id`, `PWD`, `HOME`, and `HERMES_HOME`.
3. If the paths differ, the script is environment-sensitive.

## Fix

Make cron scripts derive paths from `HERMES_HOME`:

```bash
HERMES_ROOT="${HERMES_HOME:-${HOME:-~}/.hermes}"
SRC="${HERMES_ROOT}/config.yaml"
BACKUP_DIR="${HERMES_ROOT}/backups"
```

Avoid hardcoding `/home/<user>/.hermes` in anything that runs under the scheduler.

## Prevention

- Prefer `HERMES_HOME` over `~` or `/home/...` in scheduled scripts.
- When debugging a script, test it with `HERMES_HOME` explicitly set to both the host path and the suspected container path.
- If a script must behave differently inside the scheduler, branch on `HERMES_HOME` rather than assuming a fixed filesystem layout.
