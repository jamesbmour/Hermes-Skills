---
name: python-coding-agent
description: "Use when writing, reviewing, refactoring, or scaffolding Python code — including new projects, modules, functions, classes, scripts, data pipelines, APIs, and notebooks. Also use when the user asks for Python best practices, idiomatic Python, type hints, packaging, dependency management, or project setup. Covers the full Python development lifecycle: project structure, tooling, idioms, testing strategy, code review, and refactoring. Triggers on any Python-specific coding task even if the user doesn't say 'Python' explicitly but the context is clearly Python development."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [python, coding, development, refactoring, code-review, best-practices, packaging]
    related_skills: [test-driven-development, systematic-debugging, requesting-code-review, plan]
---

# Python Coding Agent

## Overview

This skill makes the agent a strong Python development partner. It covers the full lifecycle: scaffolding projects, writing idiomatic code, choosing the right tools, reviewing for common Python pitfalls, and refactoring safely. The goal is production-quality Python that is clean, typed, tested, and maintainable.

**Core principle:** Write idiomatic, well-typed, well-tested Python. Prefer the standard library and well-maintained packages. Keep code simple and readable. Always run code to verify it works — never just describe what code would do.

## When to Use

- Writing new Python code (functions, classes, modules, scripts, APIs, pipelines)
- Scaffolding or setting up a new Python project
- Reviewing or refactoring existing Python code
- Choosing Python libraries, data structures, or patterns
- Questions about Python packaging, dependency management, or tooling
- Debugging Python code (combine with `systematic-debugging` for complex bugs)
- Writing tests for Python code (combine with `test-driven-development`)

**Don't use for:** non-Python languages, purely conceptual questions with no code involved.

---

## 1. Project Structure & Scaffolding

### Modern Python Project Layout

Use the `src/` layout for anything beyond a single throwaway script:

```
my-project/
├── pyproject.toml          # Project metadata, deps, tool config
├── README.md
├── src/
│   └── my_package/
│       ├── __init__.py
│       └── ...
├── tests/
│   ├── __init__.py
│   └── test_*.py
└── .python-version         # Optional: pin Python version (pyenv/uv)
```

### pyproject.toml — The Single Config Source

Centralize all project config in `pyproject.toml`. Use this minimal starting point and extend as needed:

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "my-package"
version = "0.1.0"
description = "Short description"
requires-python = ">=3.11"
dependencies = []

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov",
    "ruff>=0.5",
    "mypy>=1.10",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM", "C4"]

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers"
```

### When the user says "create a new Python project"

1. Create the directory structure above
2. Write `pyproject.toml` with the package name, Python version, and dev deps
3. Create `src/<package_name>/__init__.py` and `tests/__init__.py`
4. Write a minimal `README.md`
5. If the user has a virtual environment, install dev deps: `pip install -e ".[dev]"` or `uv pip install -e ".[dev]"`
6. Verify the setup: `ruff check . && mypy src/ && pytest`

### Single-File Scripts

For quick scripts, data analysis, or tutorials (the user prefers concise single-file examples), keep it simple:

- No `src/` layout needed — a single `.py` file is fine
- Use a `if __name__ == "__main__":` guard
- Type hints still recommended for function signatures
- If dependencies are needed, note them in a comment or a small `requirements.txt`

---

## 2. Tooling & Dependency Management

### Recommended Tool Stack

| Concern | Tool | Why |
|---------|------|-----|
| Linting + Formatting | `ruff` | Replaces flake8 + black + isort. Extremely fast. |
| Type checking | `mypy` (strict) or `pyright` | Catches bugs before runtime. |
| Testing | `pytest` | Industry standard, rich plugin ecosystem. |
| Coverage | `pytest-cov` | Integrated with pytest. |
| Dependency management | `uv` or `pip` + `venv` | `uv` is faster; `pip` is universal. |
| Building | `hatchling` or `setuptools` | `hatchling` is modern and simple. |

### Virtual Environments

Always use a virtual environment. Detect or create one before installing:

```bash
# Check if a venv is active
python -c "import sys; print(sys.prefix)"

# Create one if needed (standard library)
python -m venv .venv && source .venv/bin/activate

# Or with uv (faster)
uv venv && source .venv/bin/activate
```

If the user has a venv active in their session, don't create a new one — just use it.

### Dependency Installation Commands

```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Or with uv
uv pip install -e ".[dev]"

# Add a runtime dependency
# Edit pyproject.toml [project] dependencies, then:
pip install -e ".[dev]"
```

---

## 3. Writing Idiomatic Python

### Type Hints — Always Use Them

Type hints are mandatory for function signatures. They catch bugs, document intent, and enable IDE autocomplete.

```python
# Good
def parse_config(path: Path) -> dict[str, Any]:
    ...

# Bad — no hints
def parse_config(path):
    ...
```

Use modern syntax for Python 3.10+:

```python
# Modern (3.10+)
def process(items: list[str]) -> str | None: ...

# Old style — don't use unless supporting <3.10
from typing import List, Optional
def process(items: List[str]) -> Optional[str]: ...
```

### Choosing Data Structures

| Need | Use | Example |
|------|-----|---------|
| Simple data container | `@dataclass` | `@dataclass` with typed fields |
| Immutable data | `@dataclass(frozen=True)` | Coordinates, config values |
| Structured data with validation | `pydantic.BaseModel` | API models, config from YAML/JSON |
| Key-value lookup | `dict` | General purpose |
| Ordered unique items | `list` + `set` (or just `dict` in 3.7+) | |
| Named tuple-like | `NamedTuple` or `@dataclass` | Lightweight records |
| Enum-like constants | `enum.Enum` | Status codes, types |

### Dataclasses — The Default Choice

```python
from dataclasses import dataclass, field

@dataclass
class Customer:
    name: str
    email: str
    tags: list[str] = field(default_factory=list)

    def display_name(self) -> str:
        return f"{self.name} <{self.email}>"
```

Prefer `@dataclass` over `__init__` with manual assignment. It's cleaner, less boilerplate, and gives you `__repr__` and `__eq__` for free.

### Pathlib Over os.path

```python
# Good
from pathlib import Path

config_path = Path("config") / "settings.yaml"
data = config_path.read_text()
if not config_path.exists():
    config_path.mkdir(parents=True, exist_ok=True)

# Bad — string manipulation
import os
config_path = os.path.join("config", "settings.yaml")
if not os.path.exists(config_path):
    os.makedirs(config_path, exist_ok=True)
```

### Context Managers for Resource Management

```python
# Good — automatic cleanup
with open("data.csv") as f:
    reader = csv.DictReader(f)
    ...

# Custom context manager
from contextlib import contextmanager

@contextmanager
def temporary_config(overrides: dict):
    original = get_config()
    update_config(overrides)
    try:
        yield get_config()
    finally:
        update_config(original)
```

### Error Handling — Be Specific

```python
# Good — catch specific exceptions, don't swallow
try:
    result = api.fetch()
except api.ConnectionError:
    logger.warning("API unreachable, using cache")
    result = cache.get()
except api.NotFoundError as e:
    raise ValueError(f"Resource not found: {e}") from e

# Bad — catch-all that hides bugs
try:
    result = api.fetch()
except Exception:
    pass  # What went wrong? Nobody knows.
```

### Use `if __name__ == "__main__"` Guard

For any script that could be imported or run directly:

```python
def main() -> None:
    ...

if __name__ == "__main__":
    main()
```

### f-strings for String Formatting

```python
# Good
message = f"Processing {len(items)} items for {customer.name}"

# Bad
message = "Processing {} items for {}".format(len(items), customer.name)
message = "Processing " + str(len(items)) + " items for " + customer.name
```

### Comprehensions Over Map/Filter

```python
# Good
prices = [item.price for item in items if item.in_stock]
price_map = {item.sku: item.price for item in items}

# Bad
prices = list(filter(lambda i: i.in_stock, map(lambda x: x.price, items)))
```

### Structural Pattern Matching (Python 3.10+)

```python
match command:
    case ("add", item):
        cart.add(item)
    case ("remove", item):
        cart.remove(item)
    case ("checkout",):
        cart.checkout()
    case _:
        raise ValueError(f"Unknown command: {command}")
```

---

## 4. Testing Strategy

### pytest Fundamentals

```python
# tests/test_calculator.py
import pytest
from my_package.calculator import Calculator

class TestCalculator:
    @pytest.fixture
    def calc(self) -> Calculator:
        return Calculator()

    def test_add_two_numbers(self, calc: Calculator) -> None:
        assert calc.add(2, 3) == 5

    def test_add_negative_numbers(self, calc: Calculator) -> None:
        assert calc.add(-1, -2) == -3

    @pytest.mark.parametrize("a, b, expected", [
        (0, 0, 0),
        (100, 200, 300),
        (1.5, 2.5, 4.0),
    ])
    def test_add_various_inputs(self, calc: Calculator, a: float, b: float, expected: float) -> None:
        assert calc.add(a, b) == expected
```

### Test Organization

- One test file per source module: `src/my_module.py` → `tests/test_my_module.py`
- Group related tests in a class: `class TestClassName:`
- Use fixtures for shared setup — not `setUp`/`tearDown`
- Use `@pytest.mark.parametrize` for data-driven tests
- Name tests descriptively: `test_calculator_returns_zero_for_empty_input` not `test_calc1`

### When to Use TDD

For bug fixes and new features, load the `test-driven-development` skill and follow RED-GREEN-REFACTOR. For exploratory prototypes or throwaway scripts, write tests after the code is stable.

### Running Tests

```bash
# Single test
pytest tests/test_module.py::TestClass::test_method -v

# By keyword
pytest tests/ -k "test_name_pattern" -v

# With coverage
pytest tests/ --cov=src/my_package --cov-report=term-missing

# Fast feedback loop (stop at first failure)
pytest tests/ -x -q
```

---

## 5. Code Review Checklist for Python

When reviewing Python code (yours or someone else's), check these in order:

### Correctness
- [ ] Type hints on all function signatures
- [ ] Return types are correct and consistent
- [ ] Edge cases handled: empty lists, None, division by zero, empty strings
- [ ] Off-by-one errors in loops and slicing
- [ ] Mutable default arguments (the classic Python trap)
- [ ] Exception handling is specific, not bare `except:` or `except Exception:`

### The Mutable Default Argument Trap

```python
# BAD — mutable default shared across all calls
def add_item(item, items=[]):
    items.append(item)
    return items

# GOOD — use None sentinel or default_factory
def add_item(item, items: list | None = None) -> list:
    if items is None:
        items = []
    items.append(item)
    return items
```

### Idioms
- [ ] `pathlib.Path` instead of `os.path` string manipulation
- [ ] f-strings instead of `.format()` or `%` formatting
- [ ] Comprehensions instead of `map()`/`filter()` (when readable)
- [ ] `enumerate()` instead of `range(len())` when you need the index
- [ ] `zip()` instead of parallel indexing
- [ ] Context managers (`with`) for files, connections, locks
- [ ] `dataclass` instead of manual `__init__`

### Safety
- [ ] No `eval()` or `exec()` on untrusted input
- [ ] No hardcoded secrets, API keys, or passwords
- [ ] SQL uses parameterized queries, never f-string SQL
- [ ] File paths are validated or sanitized when from user input
- [ ] No `pickle.load()` on untrusted data

### Performance (check if relevant)
- [ ] O(n) loops inside O(n) loops → consider a dict/set lookup
- [ ] String concatenation in a loop → use `"".join()`
- [ ] Repeated dict/list creation in a hot path → cache or precompute
- [ ] Generator (`yield`) for large sequences instead of building a full list
- [ ] `__slots__` on dataclasses if millions of instances

---

## 6. Refactoring Patterns

### Safe Refactoring Steps

1. **Run existing tests** — confirm they pass before you start
2. **Write a test for the behavior you're about to change** — if one doesn't exist
3. **Make one change at a time** — run tests after each
4. **Use `ruff` to catch issues** — `ruff check --fix` for safe auto-fixes

### Common Refactorings

**Extract function:**
```python
# Before
def process_order(order):
    total = sum(item.price * item.qty for item in order.items)
    tax = total * 0.08
    shipping = 10.0 if total < 100 else 0.0
    return total + tax + shipping

# After
def calculate_subtotal(order) -> float:
    return sum(item.price * item.qty for item in order.items)

def calculate_fees(subtotal: float) -> float:
    tax = subtotal * 0.08
    shipping = 10.0 if subtotal < 100 else 0.0
    return tax + shipping

def process_order(order) -> float:
    subtotal = calculate_subtotal(order)
    return subtotal + calculate_fees(subtotal)
```

**Replace dict with dataclass:**
```python
# Before — dict with string keys, easy to misspell
user = {"name": "Alice", "email": "alice@example.com", "age": 30}

# After — typed, documented, IDE autocomplete
@dataclass
class User:
    name: str
    email: str
    age: int
```

**Replace conditional with polymorphism/dispatch:**
```python
# Before
def process(payment):
    if payment.type == "credit":
        ...
    elif payment.type == "paypal":
        ...
    elif payment.type == "bank":
        ...

# After — strategy pattern
PROCESSORS = {
    "credit": process_credit,
    "paypal": process_paypal,
    "bank": process_bank,
}

def process(payment):
    handler = PROCESSORS[payment.type]
    handler(payment)
```

---

## 7. Common Pitfalls

1. **Mutable default arguments** — `def f(items=[])` creates one list shared across all calls. Use `None` sentinel.

2. **Bare `except:` clauses** — Catches `KeyboardInterrupt`, `SystemExit`, and hides real bugs. Always catch specific exceptions.

3. **`is` vs `==`** — `is` checks identity, `==` checks equality. Use `is` only for `None`, `True`, `False`. Never `if x is "hello"`.

4. **Late binding in closures** — `lambdas = [lambda: i for i in range(5)]` — all return 4. Use `lambda i=i: i` or a factory.

5. **Modifying a list while iterating** — `for x in items: items.remove(x)` skips elements. Iterate over a copy: `for x in list(items):`.

6. **Confusing `datetime.now()` and `datetime.utcnow()`** — Prefer `datetime.now(timezone.utc)` for timezone-aware datetimes. `datetime.utcnow()` is deprecated in 3.12+.

7. **Not using `__all__` in package `__init__.py`** — Without `__all__`, `from package import *` imports everything. Define the public API explicitly.

8. **Ignoring `pyproject.toml` in favor of scattered configs** — Keep all tool config in one place. Ruff, mypy, and pytest all read from `pyproject.toml`.

9. **Using `os.system()` or `subprocess` with shell=True on untrusted input** — Shell injection risk. Use `subprocess.run([...], shell=False)` with argument lists.

10. **Forgetting `encoding="utf-8"` when opening files** — On some systems, the default encoding is not UTF-8. Always specify: `open(path, encoding="utf-8")`.

---

## 8. Integration with Other Skills

### test-driven-development
Load this skill when writing new features or fixing bugs. Follow RED-GREEN-REFACTOR for Python code.

### systematic-debugging
Load this skill for complex Python bugs. Use the tight feedback loop with `pytest` as the reproduction command.

### requesting-code-review
Load this skill before committing Python code. Run `ruff check`, `mypy`, and `pytest` as pre-commit gates.

### plan
Load this skill for larger Python projects (multi-file, multi-day). Write a plan to `.hermes/plans/` before coding.

---

## 9. Workflow: A Complete Python Feature

Here's the full workflow for implementing a Python feature from scratch:

1. **Understand the task** — What does the code need to do? What are the inputs and outputs?
2. **Check for existing project structure** — Is there a `pyproject.toml`? A `src/` layout? Tests?
3. **If new project:** scaffold using the structure in Section 1.
4. **Write a test** (TDD) — Write the test first, run it, watch it fail.
5. **Write minimal implementation** — Simplest code that passes the test.
6. **Run linter and type checker:**
   ```bash
   ruff check src/ tests/
   ruff format --check src/ tests/
   mypy src/
   ```
7. **Run tests:**
   ```bash
   pytest tests/ -v
   ```
8. **Refactor** — Clean up, extract helpers, improve names. Keep tests green.
9. **Review against the checklist** in Section 5.
10. **Run the code** — Actually execute it. Never just describe what it would do. Use the `terminal` tool to run it and verify output.

---

## Verification Checklist

- [ ] All function signatures have type hints
- [ ] `ruff check` passes with no errors
- [ ] `ruff format --check` passes (or run `ruff format` to fix)
- [ ] `mypy` passes (or `pyright`) with no errors
- [ ] `pytest` passes with no warnings
- [ ] Code actually runs — verified via `terminal` tool
- [ ] No mutable default arguments
- [ ] No bare `except:` clauses
- [ ] No hardcoded secrets or `eval()`/`exec()` on untrusted input
- [ ] Uses `pathlib.Path` for file operations
- [ ] Uses f-strings for string formatting
- [ ] Uses `@dataclass` for data containers
- [ ] `pyproject.toml` is the single config source
- [ ] Tests use `pytest` with descriptive names and fixtures