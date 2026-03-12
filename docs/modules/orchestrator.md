# orchestrator.md — Orchestrator Node

> **Status:** Stub — to be completed in step 16 (`docs: full documentation pass`).

---

## Purpose

The orchestrator is the **only** node that generates text the user hears. It is the sole user-facing agent. It receives the accumulated conversation history, the current transcript or proactive message, and any error condition, then calls the configured LLM to either:

1. **Delegate to a subagent:** Sets `intent` in the returned dict. Does not set `response`. The conditional edge routes to `route`.
2. **Produce a final answer:** Sets `response` in the returned dict. Clears `intent`. The conditional edge routes to `respond`.

---

## State Contract

| Direction | Field | Value |
|---|---|---|
| Input | `messages` | Full message history |
| Input | `transcript` | Current user utterance (or `None` in proactive turn) |
| Input | `proactive_message` | Proactive prompt (or `None` in reactive turn) |
| Input | `error` | Last error string (or `None`) |
| Output | `messages` | Appended with new AI message |
| Output | `intent` | Intent label string — **xor** with `response` |
| Output | `response` | Final spoken text — **xor** with `intent` |

---

## System Prompt Rules

Configured in `config.yaml` under `llm.system_prompt`. The prompt must:

- Instruct the model to be concise — responses are spoken aloud.
- Instruct the model never to reveal that background agents exist.
- Describe available subagents (by description, not name) so the model knows when to delegate.
- Handle `proactive_message` as the initiating prompt when `transcript` is absent.
- Handle `error` conditions: surface user-friendly errors or silently continue.

---

## Proactive Behavior

When `state["proactive_message"]` is set (by the `scheduler` node), the orchestrator uses it as the initiating prompt instead of the user transcript. It generates a natural message, sets `response`, and the graph flows to `respond` → TTS → `listen`. This is the mechanism for all Renix-initiated interactions.

---

## Security Notes

- Transcripts are **never** logged at INFO level or above.
- LLM responses are **never** logged at INFO level or above.
- The system prompt explicitly instructs the model not to reveal agent internals.
