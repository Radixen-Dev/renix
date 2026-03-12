# AGENTS.md — AI Agent Contributor Rules

> **These rules apply to every AI agent working on this codebase.**  
> Read this file in full before writing any code. Read it before opening any PR.  
> Status: Stub — to be completed in step 17 (`feat(repo): CONTRIBUTING.md + AGENTS.md`).

---

## Mandatory Pre-Work

- Before writing any code, read the relevant doc in `docs/modules/`.
- Before writing any node, read `docs/modules/graph.md` completely.
- Before writing any subagent, read `docs/modules/agents.md` completely.
- Before writing any tool, read `docs/modules/tools.md` completely.

## Hard Rules

1. **Never modify `core/state.py` or `core/interfaces.py` without an approved GitHub issue first.**
2. **Never add a node to `core/graph.py` without a corresponding entry in `docs/architecture.md`.**
3. **Never add a subagent without a corresponding section in `docs/modules/agents.md`.**
4. **Never add a tool without a corresponding section in `docs/modules/tools.md`.**
5. **Never hardcode secrets, API keys, model names, or device IDs.** They go in `config/config.yaml` or `.env`.
6. **Never use `except: pass`.** Always catch, log with context, and surface to `state["error"]`.
7. **Never mutate `GraphState` in place.** Nodes return partial dicts of updates.
8. **Never log audio bytes, transcripts, or LLM responses at INFO level or above.**
9. **Never work directly on `main`.** Always branch → PR → review → merge.
10. **Never open a PR without running `pytest`, `ruff check .`, and `mypy .` first.**

## Pre-PR Checklist

Before opening any PR, verify every item:

- [ ] No dead code or unused imports
- [ ] No hardcoded secrets or configuration values
- [ ] All public functions/classes have docstrings with type hints
- [ ] `from __future__ import annotations` at top of every file
- [ ] GraphState not mutated in place — nodes return partial dicts
- [ ] State contract documented for any new or modified node
- [ ] Module or agent doc in `docs/modules/` updated
- [ ] `docs/architecture.md` updated if graph structure changed
- [ ] All tests pass (`pytest`)
- [ ] Linting passes (`ruff check .`)
- [ ] Type checking passes (`mypy .`)
- [ ] Synced with main before this PR (`git pull origin main`)
- [ ] One issue addressed — no bundled unrelated changes

## Import Rules

```
core/       → imports nothing from modules/
modules/**  → imports only from core/
agents      → imports from core/ and modules/ (not from other agents)
graph.py    → the only file that imports from modules/agents/
```

Circular imports are forbidden. Violating the import topology is a rejected PR.
