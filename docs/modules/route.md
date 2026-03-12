# route.md — Intent Classification and Subagent Dispatch

> **Status:** Stub — to be completed in step 16 (`docs: full documentation pass`).

---

## Purpose

The `route` node is a conditional edge function. It reads `state["intent"]` (set by the orchestrator) and returns the name of the subagent node to dispatch to.

It does not modify state itself — the orchestrator sets `intent`, the conditional edge calls `route_after_orchestrator` to decide the next node, and `route` maps the intent string to a node name.

---

## Dispatch Table

| Intent label | Routes to | Subagent |
|---|---|---|
| `tool_use` | `tool_use` | `ToolUseAgent` |
| `memory` | `memory` | `MemoryAgent` |
| `mcp` | `mcp` | `MCPAgent` |
| *(unknown)* | `orchestrator` | *(fallback — no subagent)* |

This table is maintained in `core/nodes/route.py` as `INTENT_DISPATCH`. Update it whenever a new subagent is registered.

---

## Adding a New Intent

1. Register the subagent in `modules/agents/__init__.py`.
2. Add a new entry to `INTENT_DISPATCH` in `core/nodes/route.py`.
3. Add the intent label to this table.
4. Update `docs/modules/agents.md` with the new subagent section.
