# Contributing to Renix

> **Status:** Stub — to be completed in step 17 (`feat(repo): CONTRIBUTING.md + AGENTS.md`).

---

## Development Environment Setup

```bash
git clone https://github.com/radixen/renix.git
cd renix
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / Raspberry Pi
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp config/.env.example .env
```

## Branch Naming

| Type | Pattern | Example |
|---|---|---|
| Feature | `feat/<scope>-<description>` | `feat/audio-device-fallback` |
| Bug fix | `fix/<scope>-<description>` | `fix/stt-empty-transcript` |
| Documentation | `docs/<description>` | `docs/agents-mcp-section` |

## Commit Format

Conventional Commits:

```
feat(scope): short description

Longer explanation if needed. References #issue.
```

## PR Requirements

- One issue per PR — no bundled unrelated changes.
- `git pull origin main` and resolve conflicts **on your branch** before opening.
- All checklist items in `.github/PULL_REQUEST_TEMPLATE.md` must be checked.
- No PR merges without passing `pytest`, `ruff check .`, and `mypy .`.

## Running Tests

```bash
pytest                          # all tests with coverage
pytest tests/unit/              # unit tests only
pytest tests/integration/       # integration tests only
ruff check .                    # linting
mypy .                          # type checking
```

## Adding a Tool

<!-- TODO (step 17): Step-by-step guide. Summary: new ToolPlugin file → add to TOOLS → doc. -->

## Adding a Subagent

<!-- TODO (step 17): Step-by-step guide. Summary: new SubagentPlugin file → add to AGENTS → intent label in route.py → doc. -->
