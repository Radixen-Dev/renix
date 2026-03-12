# graph.md — Parent Graph

> **Status:** Stub — to be completed in step 16 (`docs: full documentation pass`).  
> Updated whenever `core/graph.py` or any node changes.

---

## Overview

`core/graph.py` builds and compiles the parent `StateGraph`. It wires all node functions, registers subagent subgraphs as nodes, defines all edges (including conditional edges), attaches `MemorySaver`, and returns the compiled graph to `main.py`.

---

## GraphState Schema

| Field | Type | Set by | Description |
|---|---|---|---|
| `messages` | `Annotated[list, add_messages]` | All LLM nodes | Full message history |
| `transcript` | `Optional[str]` | `transcribe` | Current user utterance |
| `response` | `Optional[str]` | `orchestrator` | Final text to speak |
| `intent` | `Optional[str]` | `orchestrator` | Classified intent for routing |
| `active_subagent` | `Optional[str]` | `route` | Name of running subagent |
| `audio_bytes` | `Optional[bytes]` | `listen` → cleared by `transcribe` | Raw PCM audio |
| `proactive_message` | `Optional[str]` | `scheduler` | Message for proactive turn |
| `error` | `Optional[str]` | Any node on failure | Last error string |

---

## Nodes

### listen

- **Purpose:** Block until wake word detected; record one utterance; reset turn state.
- **State inputs:** (none — resets fields)
- **State outputs:** `audio_bytes`, `transcript=None`, `response=None`
- **Edges:** → `transcribe` (always)
- **Side effects:** Calls `WakeWordDetector.wait_for_detection()`, `AudioRecorder.record()`
- **Error handling:** Sets `state["error"]`; returns to listen loop on `AudioError` / `WakeWordError`.

### transcribe

- **Purpose:** Convert raw PCM audio to text.
- **State inputs:** `audio_bytes`
- **State outputs:** `transcript` (str), `audio_bytes=None`
- **Edges:** → `orchestrator` (always)
- **Side effects:** Calls `Transcriber.transcribe(audio_bytes)`
- **Error handling:** Sets `state["error"]` on `TranscriptionError`; `transcript` set to empty string.

### orchestrator

- **Purpose:** Sole user-facing LLM node. Generates response or delegates to subagent.
- **State inputs:** `messages`, `transcript`, `proactive_message`, `error`
- **State outputs:** `messages` (appended), either `intent` or `response`
- **Edges:** → `route` (intent set) | → `respond` (response set)
- **Side effects:** One LLM API call.
- **Error handling:** Sets `state["error"]` on `LLMError`.

### route

- **Purpose:** Conditional edge — maps `intent` to subagent node name.
- **State inputs:** `intent`
- **State outputs:** `active_subagent`
- **Edges:** → `[agent.name]` per `INTENT_DISPATCH`
- **Side effects:** None.
- **Error handling:** Falls back to `orchestrator` on unknown intent.

### respond

- **Purpose:** Speak the final response via TTS.
- **State inputs:** `response`
- **State outputs:** (none)
- **Edges:** → `listen` (always)
- **Side effects:** Calls `Speaker.speak(response)`
- **Error handling:** Sets `state["error"]` on `TTSError`.

### scheduler

- **Purpose:** Proactive entry point — constructs a `proactive_message`.
- **State inputs:** (none — graph entry point)
- **State outputs:** `proactive_message`, `transcript=None`, `intent=None`
- **Edges:** → `orchestrator` (always)
- **Side effects:** Reads config; may query recent conversation summary.
- **Error handling:** Sets `state["error"]` on `ConfigError`.
