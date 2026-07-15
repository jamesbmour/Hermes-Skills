# Profile Customization Guide

Profiles isolate Hermes sessions with separate configs, skills, memory, and personality. Create specialized profiles for different workflows.

## Creating Profiles

```bash
# Create a profile (copies everything from default)
hermes profile create <name> --clone-all

# Create with a specific alias
hermes profile create <name> --clone-all
hermes profile alias <name> --name <alias>
```

## Key Customization Files

Each profile lives in `~/.hermes/profiles/<name>/`:

| File | Purpose |
|------|---------|
| `config.yaml` | Model, provider, toolsets, terminal settings |
| `.env` | Profile-specific API keys |
| `SOUL.md` | Agent personality and task-specific instructions |
| `AGENTS.md` | Project context loaded when cwd is in that directory |
| `skills/config.yaml` | Enable/disable skills per profile |
| `memory/` | Profile-specific persistent memory |

## SOUL.md — Agent Personality

The personality file that loads into every session. Use for:
- Coding style preferences (e.g., "prefer pathlib over os.path")
- Output format expectations (e.g., "be concise, show code examples")
- Domain-specific conventions (e.g., "use pytest, not unittest")

```markdown
# Python Development Profile

You are a Python development specialist.

## Code Quality
- Use type hints for function signatures
- Prefer composition over inheritance
- Keep functions small and focused

## Libraries
- Web: FastAPI for APIs
- Testing: pytest with pytest-asyncio
- Linting: ruff (fast, all-in-one)
```

## AGENTS.md — Project Context

Loaded when Hermes runs in that directory. Use for:
- Project discovery patterns (where to find configs, tests)
- Standard commands (how to run tests, format code)
- Project-type specific guidance

```markdown
## Project Discovery
- Check for `pyproject.toml`, `setup.py`, or `requirements.txt`
- Look for `.python-version` or `pyvenv.cfg`

## Common Commands
\`\`\`bash
pytest tests/ -v
ruff format .
mypy src/
\`\`\`
```

## skills/config.yaml — Skill Selection

Enable specific skills per profile:

```yaml
software-development:
  - python-debugpy
  - test-driven-development
  - systematic-debugging

# Optional domains
# data-science:
#   - jupyter-live-kernel
```

## config.yaml — Settings

Common profile-specific overrides:

```yaml
# Terminal working directory
terminal:
  cwd: ~/projects

# Model for this profile
model:
  default: anthropic/claude-sonnet-4
  provider: openrouter

# Enable specific toolsets
toolsets:
  - web
  - terminal
  - file
  - code_execution
```

## Cross-Profile Edits

When editing another profile's files from a different session, use `cross_profile=True` to bypass the guard:

```python
write_file(
    path="/Users/you/.hermes/profiles/python/skills/config.yaml",
    content="...",
    cross_profile=True
)
```

## Use Cases

| Profile Type | SOUL.md Focus | AGENTS.md Focus |
|--------------|---------------|------------------|
| Python dev | PEP 8, testing, modern idioms | venv activation, pytest commands |
| Data science | Notebooks, visualization, pandas patterns | Data directories, Jupyter setup |
| DevOps | Infrastructure as code, safety checks | Deploy commands, environment files |
| Frontend | Component patterns, accessibility | Build commands, framework conventions |

## Aliases

Aliases create shell shortcuts in `~/.local/bin/`:

```bash
# Set alias
hermes profile alias python --name py

# Use
py              # Starts hermes -p python chat
py -q "task"    # One-shot query
```

Note: If the alias conflicts with an existing command (like `python`), choose a different name (e.g., `py`).