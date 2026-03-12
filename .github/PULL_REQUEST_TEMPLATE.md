## What does this PR do?
<!-- One sentence describing the change. -->

## Related issue
Closes #

## Checklist
- [ ] No dead code or unused imports
- [ ] No hardcoded secrets or configuration values
- [ ] All public functions/classes have docstrings with type hints
- [ ] `from __future__ import annotations` at the top of every new/modified file
- [ ] GraphState not mutated in place — nodes return partial dicts
- [ ] State contract documented for any new or modified node
- [ ] Module or agent doc in `docs/modules/` updated
- [ ] `docs/architecture.md` updated if graph structure changed
- [ ] All tests pass (`pytest`)
- [ ] Linting passes (`ruff check .`)
- [ ] Type checking passes (`mypy .`)
- [ ] Synced with main before this PR was opened (`git pull origin main`)
- [ ] One issue addressed — no bundled unrelated changes
