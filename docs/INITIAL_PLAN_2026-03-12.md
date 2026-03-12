# Renix — Agent Build Plan
Developed by Radixen.

> **Read this entire document before writing a single line of code.**
> This is the authoritative specification for the Renix project. Every architectural decision, naming convention, file location, and process rule described here is a requirement, not a suggestion. Deviations require explicit justification in a GitHub issue before implementation.

---

## 0. Non-Negotiables

These rules apply to every task, every PR, every file, forever:

1. **No dead code.** Every function, import, class, and variable must be used. Delete anything unused before opening a PR.
2. **No redundancy.** One function does one thing. Shared logic belongs in `core/utils.py`, never duplicated across modules.
3. **No hardcoded secrets or configuration.** API keys, endpoints, model names, device IDs — everything configurable goes in `config/config.yaml` or `.env`. No exceptions.
4. **No silent failures.** Every exception must be caught, logged with context, and either recovered from gracefully or re-raised with a descriptive message. Never `except: pass`.
5. **No undocumented changes.** Every PR touching a node, module, or agent must update the corresponding doc file. PRs without documentation updates are rejected without review.
6. **No work on `main`.** Branch → PR → review → merge. Always. Direct pushes to `main` are blocked.
7. **No merge without syncing.** Before opening a PR, `git pull origin main` and resolve all conflicts on your branch — not in the PR.
8. **No mutation of `GraphState` outside node functions.** Nodes receive state, return a partial dict of updates. They never mutate the object passed to them.
9. **No circular imports.** `core/` imports nothing from `modules/`. Modules import only from `core/`. Agents import from `core/` and `modules/`. Nothing imports from `modules/agents/` except `core/graph.py`.

---

## 1. Project Overview

**Renix** is a locally-running, modular AI voice assistant orchestrated by **LangGraph**. It listens for a wake word, transcribes speech, routes the turn through a compiled LangGraph agent graph, and speaks the response — all with a plugin architecture that allows new agents and tools to be added without modifying any existing code.

### Core design philosophy

- **LangGraph owns orchestration.** The compiled `StateGraph` owns the full turn lifecycle. There is no custom event bus, no hand-rolled orchestration loop. Graph edges are control flow; `GraphState` is the single source of truth per turn.
- **One user-facing agent.** The orchestrator agent is the only entity the user ever interacts with — for both reactive (user speaks) and proactive (Renix initiates) conversations. Subagents run silently in the background, return results into state, and the orchestrator decides what to say. The user never knows subagents exist.
- **Agents and tools are plugins.** Adding a subagent means creating one file and one registration line. Adding a tool means the same. No changes to the graph, the orchestrator, or any existing node or agent.
- **Nodes are pure functions.** Every graph node has the signature `(state: GraphState, config: RunnableConfig) -> dict`. No side effects except documented I/O calls. Fully testable in isolation.
- **I/O modules are thin adapters.** Audio, STT, TTS, and wake word modules are not graph participants. They are called by specific nodes, return data, and that data enters state. They are interface-backed and independently replaceable.
- **Documentation is not optional.** It is part of the feature. A node, agent, or module without complete documentation is an incomplete PR.
- **Cross-platform.** Runs on Raspberry Pi OS (Bookworm, 64-bit, ARM) and Windows 10/11. All platform-specific handling lives exclusively in `modules/audio/device_manager.py`.

---

## 2. Repository Structure

```
renix/
├── core/
│   ├── __init__.py
│   ├── graph.py               # Builds and compiles the parent StateGraph
│   ├── state.py               # GraphState TypedDict — the single state schema
│   ├── interfaces.py          # Abstract base classes for all plugins and I/O modules
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── listen.py          # Awaits wake word + records audio into state
│   │   ├── transcribe.py      # Calls STT module, writes transcript to state
│   │   ├── route.py           # Conditional edge — classifies intent, selects subagent
│   │   ├── orchestrator.py    # Orchestrator agent — sole user-facing LLM node
│   │   ├── respond.py         # Calls TTS with final response from state
│   │   └── scheduler.py       # Proactive initiation entry point
│   └── utils.py               # Logging factory, config loader, shared exceptions
│
├── modules/
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── device_manager.py  # Autodiscover and validate input/output devices
│   │   └── recorder.py        # Mic capture — returns raw PCM bytes
│   │
│   ├── wake_word/
│   │   ├── __init__.py
│   │   └── detector.py        # openWakeWord wrapper
│   │
│   ├── stt/
│   │   ├── __init__.py
│   │   └── transcriber.py     # faster-whisper wrapper
│   │
│   ├── tts/
│   │   ├── __init__.py
│   │   └── speaker.py         # pyttsx3 wrapper
│   │
│   ├── tools/
│   │   ├── __init__.py        # TOOLS list — register all ToolPlugin instances here
│   │   ├── registry.py        # Converts ToolPlugin instances to LangChain tools
│   │   └── builtin/
│   │       ├── __init__.py
│   │       ├── time_tool.py
│   │       └── weather_tool.py
│   │
│   └── agents/
│       ├── __init__.py        # AGENTS list — register all SubagentPlugin instances here
│       ├── tool_use_agent.py  # Subagent: multi-step tool execution via ToolNode
│       ├── memory_agent.py    # Subagent: long-term memory recall and storage
│       └── mcp_agent.py       # Subagent: MCP server proxy tools
│
├── config/
│   ├── config.yaml            # All non-secret configuration
│   └── .env.example           # Secret key template — never commit real values
│
├── data/
│   └── .gitkeep               # Runtime data directory (memory DB, etc.) — not committed
│
├── logs/
│   └── .gitkeep               # Log output directory — not committed
│
├── docs/
│   ├── architecture.md        # System architecture + diagrams (ALWAYS KEPT CURRENT)
│   ├── CONTRIBUTING.md        # Human contributor rules
│   ├── AGENTS.md              # AI agent contributor rules (mirrors CONTRIBUTING)
│   ├── adr/
│   │   ├── 0001-langgraph-as-orchestrator.md
│   │   ├── 0002-single-user-facing-agent.md
│   │   └── 0003-openai-compat-api.md
│   └── modules/
│       ├── graph.md           # Parent graph: nodes, edges, state schema, entry points
│       ├── orchestrator.md    # Orchestrator agent node — behavior, prompt, routing logic
│       ├── scheduler.md       # Proactive initiation — triggers, config, behavior
│       ├── route.md           # Intent classification + subagent dispatch table
│       ├── agents.md          # Subagent plugin system + how to add a subagent
│       ├── tools.md           # Tool plugin system + how to add a tool
│       ├── audio.md
│       ├── wake_word.md
│       ├── stt.md
│       └── tts.md
│
├── tests/
│   ├── unit/
│   │   ├── test_state.py
│   │   ├── test_route_node.py
│   │   ├── test_tool_registry.py
│   │   ├── test_agent_registry.py
│   │   └── test_device_manager.py
│   └── integration/
│       ├── test_graph_reactive.py    # Full reactive turn with mocked I/O
│       └── test_graph_proactive.py   # Proactive initiation path
│
├── .github/
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── ISSUE_TEMPLATE/
│       ├── bug_report.md
│       └── feature_request.md
│
├── main.py
├── requirements.txt           # Exact pinned versions (==)
├── requirements-dev.txt       # pytest, ruff, mypy
├── pyproject.toml             # Ruff + mypy configuration
├── .gitignore
└── README.md
```

---

## 3. Architecture

### 3.1 GraphState

`core/state.py` defines the single shared state schema. Every node reads from and writes partial updates to this object. No code outside a node function may create or modify state.

```python
# core/state.py
from __future__ import annotations
from typing import Annotated, Optional
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    # Conversation
    messages: Annotated[list, add_messages]  # full message history (LangChain messages)
    transcript: Optional[str]                 # current user utterance, set by transcribe
    response: Optional[str]                   # final text to speak, set by orchestrator

    # Routing
    intent: Optional[str]                     # classified intent label, set by route
    active_subagent: Optional[str]            # name of subagent currently executing

    # Audio
    audio_bytes: Optional[bytes]              # raw PCM from recorder — CLEARED after STT

    # Proactive initiation
    proactive_message: Optional[str]          # set by scheduler to bypass listen/transcribe

    # Error propagation
    error: Optional[str]                      # last error message; orchestrator reads this
```

**Rules:**
- Never add fields to `GraphState` without updating `docs/modules/graph.md` in the same PR.
- `audio_bytes` must be set to `None` by the `transcribe` node after use. Raw audio must never be persisted to `MemorySaver`.
- `messages` uses the `add_messages` reducer — LangGraph handles merging correctly. Nodes return new messages to append; they never replace the full list.
- `response` and `transcript` must be reset to `None` at the start of each new turn by the `listen` node.

### 3.2 Parent Graph (`core/graph.py`)

The parent `StateGraph` is built and compiled once at startup. It wires all node functions, registers subagent subgraphs as nodes, defines all edges (including conditional edges), attaches `MemorySaver`, and returns the compiled graph to `main.py`.

**Entry points:**

```
Reactive:   __start__  →  listen
Proactive:  __start__  →  scheduler        (triggered externally by APScheduler)
```

**Reactive turn flow:**
```
listen → transcribe → orchestrator → route → [subagent] → orchestrator → respond → listen
                                           ↘ (no subagent needed)      ↗
                                             orchestrator → respond → listen
```

**Proactive turn flow:**
```
scheduler → orchestrator → respond → listen
```

**Conditional edges:**
- `orchestrator` → `route`: when `state["intent"]` is set (subagent needed).
- `orchestrator` → `respond`: when `state["response"]` is set (ready to speak).
- `route` → `[agent.name]`: maps `state["intent"]` to the registered subagent node.
- Any subagent → `orchestrator`: always, on completion. The orchestrator synthesizes and responds.

**Checkpointing:**
```python
graph.compile(checkpointer=MemorySaver())
```
Each conversation session uses a stable `thread_id` generated at startup and persisted in `data/session.json`. This gives full turn-to-turn memory at no code cost. Long-term cross-session memory is handled by the `memory_agent` subagent, not the checkpointer.

### 3.3 Orchestrator Agent Node (`core/nodes/orchestrator.py`)

The orchestrator is the only node that generates text the user hears. It is the sole user-facing agent. It:

1. Reads `messages`, `transcript`, `proactive_message`, and `error` from state.
2. Calls the configured LLM via LangChain's `ChatOpenAI` pointed at the OpenAI-compatible endpoint.
3. If the LLM's response includes a tool/subagent delegation decision: sets `intent` in the returned dict, does not set `response` → graph routes to `route`.
4. If the LLM produces a final response: sets `response` in the returned dict, clears `intent` → graph routes to `respond`.

**System prompt rules (enforced in `config.yaml`):**
- The orchestrator is explicitly instructed to never reveal that background agents exist.
- It is instructed to be concise — responses are spoken aloud, not read.
- It may initiate conversation when `proactive_message` is set.
- It reads `state["error"]` and decides whether to surface an error to the user or silently handle it.

**Proactive behavior:** When `state["proactive_message"]` is set (by the `scheduler` node), the orchestrator uses it as its prompt instead of the user transcript. It generates a natural message, sets `response`, and the graph proceeds to `respond`. This is how Renix starts conversations — timers, reminders, contextual nudges — without the user saying anything.

### 3.4 Subagent Plugin System

Every subagent implements `SubagentPlugin` from `core/interfaces.py`:

```python
# core/interfaces.py (relevant excerpt)

from abc import ABC, abstractmethod
from langgraph.graph import StateGraph

class SubagentPlugin(ABC):
    name: str           # unique string — must match intent labels dispatched by route node
    description: str    # explains to the orchestrator when to delegate to this agent

    @abstractmethod
    def build(self) -> StateGraph:
        """Build and return a compiled subgraph. Called once at startup."""
        ...
```

**Agent registry** (`modules/agents/__init__.py`):
```python
from .tool_use_agent import ToolUseAgent
from .memory_agent import MemoryAgent
from .mcp_agent import MCPAgent

AGENTS: list[SubagentPlugin] = [
    ToolUseAgent(),
    MemoryAgent(),
    MCPAgent(),
]
```

`core/graph.py` iterates `AGENTS`, calls `.build()` on each, and registers the compiled subgraph with `graph.add_node(agent.name, agent.build())`. The `route` node maps `state["intent"]` to `agent.name` via a conditional edge function.

**Adding a new subagent — complete process (no other files change):**
1. Create `modules/agents/my_agent.py` implementing `SubagentPlugin`.
2. Add to `AGENTS` in `modules/agents/__init__.py`.
3. Add the intent label(s) it handles to the dispatch table in `core/nodes/route.py`.
4. Document in `docs/modules/agents.md` with: purpose, intent labels, subgraph topology diagram, state contract.

### 3.5 Tool Plugin System

Tools implement `ToolPlugin` from `core/interfaces.py`:

```python
class ToolPlugin(ABC):
    name: str
    description: str    # used by LangChain to generate the tool schema for the LLM

    @abstractmethod
    def run(self, **kwargs) -> str:
        """Execute the tool. Return a plain string result."""
        ...
```

`modules/tools/registry.py` converts `ToolPlugin` instances to LangChain `@tool`-decorated callables. The `tool_use_agent` subgraph binds this list to a `ToolNode`, enabling automatic multi-step tool chains (LLM → tool → LLM → tool → LLM → END) via LangGraph's built-in loop.

**Adding a new tool — complete process (no other files change):**
1. Create `modules/tools/builtin/my_tool.py` implementing `ToolPlugin`.
2. Add to `TOOLS` in `modules/tools/__init__.py`.
3. Document in `docs/modules/tools.md`.

### 3.6 Proactive Initiation (`core/nodes/scheduler.py`)

The scheduler node is a separate graph entry point. It is triggered by APScheduler running in a background thread inside `main.py`. When fired:

1. It constructs a `proactive_message` string based on the configured prompt and any context it gathers (time of day, recent conversation summary, etc.).
2. It returns `{"proactive_message": message, "transcript": None, "intent": None}`.
3. The graph transitions directly to the `orchestrator` node.
4. The orchestrator generates a natural spoken message, sets `response`, and the graph flows to `respond` → TTS → speaker → `listen`.

This is the mechanism for all Renix-initiated interactions. The scheduler's cron schedule and proactive prompt are both configurable in `config.yaml`. Setting `orchestrator.proactive_enabled: false` disables it entirely.

### 3.7 I/O Module Interface Contracts

The audio stack is called by specific nodes, not part of the graph topology:

| Node | Module called | Data written to state |
|---|---|---|
| `listen` | `WakeWordDetector.wait()`, `recorder.record()` | `audio_bytes` |
| `transcribe` | `Transcriber.transcribe(audio_bytes)` | `transcript`; sets `audio_bytes: None` |
| `respond` | `Speaker.speak(response)` | nothing (side effect only) |

```python
# core/interfaces.py (I/O contracts)

class WakeWordDetector(ABC):
    @abstractmethod
    def start(self) -> None: ...
    @abstractmethod
    def stop(self) -> None: ...
    @abstractmethod
    def wait_for_detection(self) -> None:
        """Block until wake word is detected."""
        ...

class Transcriber(ABC):
    @abstractmethod
    def transcribe(self, audio_data: bytes) -> str: ...

class Speaker(ABC):
    @abstractmethod
    def speak(self, text: str) -> None: ...
```

Swapping any I/O implementation requires only a new class implementing the interface and a config change. No graph changes, no node changes.

### 3.8 Configuration Schema

```yaml
# config/config.yaml

llm:
  base_url: "http://localhost:1234/v1"    # OpenAI-compat endpoint
  model: "mistral-7b-instruct"
  system_prompt: "You are Renix, a concise voice assistant. Responses are spoken aloud."
  max_tokens: 512
  temperature: 0.7

orchestrator:
  proactive_enabled: true
  proactive_schedule: "0 * * * *"         # cron — hourly by default
  proactive_prompt: "Check if there is anything timely or useful to tell the user."

stt:
  model_size: "base"                      # tiny | base | small | medium | large
  device: "cpu"                           # cpu | cuda
  language: "en"

tts:
  rate: 175
  volume: 1.0
  voice_id: null                          # null = system default

wake_word:
  model_path: "hey_renix"
  threshold: 0.5
  cooldown_seconds: 2

memory:
  long_term_enabled: true
  db_path: "data/memory.db"

audio:
  input_device: null                      # null = system default, or name/index
  output_device: null
  sample_rate: 16000
  chunk_size: 1024

logging:
  level: "INFO"
  log_to_file: true
  log_file: "logs/renix.log"
```

`.env` holds secrets only:
```
LLM_API_KEY=
WEATHER_API_KEY=
```

---

## 4. Documentation Standards

> Documentation is not optional. It is part of the feature. An undocumented node, agent, or module is an incomplete PR and will not be merged.

### 4.1 Code-level documentation

Every public function and class requires a docstring with: what it does (imperative mood), parameters, return value, exceptions raised, and any side effects. Type hints are mandatory on all function signatures. Use `from __future__ import annotations` at the top of every file.

```python
def transcribe(self, audio_data: bytes) -> str:
    """Transcribe raw PCM audio bytes to text using faster-whisper.

    Args:
        audio_data: Raw 16kHz mono PCM audio as bytes.

    Returns:
        Transcribed text string. Empty string if no speech detected.

    Raises:
        TranscriptionError: If the model fails to process the audio.
    """
```

Private methods (`_name`) require a one-line comment explaining purpose if it isn't obvious from the name alone.

### 4.2 Node documentation (in `docs/modules/graph.md`)

Each graph node section must document:
1. **Purpose** — what this node does in the graph.
2. **State inputs** — which `GraphState` fields it reads.
3. **State outputs** — which fields it writes and what values they take.
4. **Edges** — which nodes it can transition to and under what conditions.
5. **Side effects** — any I/O calls (audio, network, disk).
6. **Error handling** — how failures are surfaced in state.

### 4.3 Subagent documentation (in `docs/modules/agents.md`)

Each subagent section must document:
1. **Purpose** — what problem this agent solves.
2. **Intent labels** — which strings from the `route` node dispatch here.
3. **Subgraph topology** — Mermaid diagram of internal nodes and edges.
4. **Tools bound** — which tool plugins this agent uses.
5. **State contract** — what it reads from `GraphState`, what it writes back.
6. **How to extend** — how to add capabilities without breaking other agents.

### 4.4 Architecture document (`docs/architecture.md`)

This is the single source of truth for the full system. Must always contain:
1. **System diagram** — Mermaid diagram of the parent graph: all nodes, edges, conditional branches, subagent boundaries. **Updated in any PR that changes graph structure.**
2. **Reactive turn sequence** — sequence diagram from wake word to spoken response.
3. **Proactive turn sequence** — sequence diagram of scheduler-initiated turn.
4. **Node index** — table of all nodes, their role, link to doc section.
5. **Agent index** — table of all registered subagents, their intent labels, link to doc.
6. **Extension guide** — step-by-step: how to add a subagent, how to add a tool.
7. **Security model** — where secrets live, what is and isn't logged, how to report vulnerabilities.

### 4.5 ADRs (`docs/adr/`)

Required for v0.1:
- `0001-langgraph-as-orchestrator.md` — why LangGraph replaces a custom orchestrator.
- `0002-single-user-facing-agent.md` — why the orchestrator is the only agent that speaks to the user.
- `0003-openai-compat-api.md` — why OpenAI-compatible format over model-specific SDKs.

Format:
```markdown
# ADR-NNNN: Title

**Date:** YYYY-MM-DD
**Status:** Accepted

## Context
Why did this decision need to be made?

## Decision
What was decided?

## Consequences
What does this make easier? What does it make harder?
```

### 4.6 CONTRIBUTING.md and AGENTS.md

`CONTRIBUTING.md`: dev environment setup, branch naming (`feat/`, `fix/`, `docs/`), conventional commit format, PR requirements, sync-before-PR rule, one-issue-per-PR rule, how to add a tool, how to add a subagent, how to run the test suite.

`AGENTS.md` is the same rules rewritten as direct imperatives for an LLM context window. Explicitly includes:
- "Before writing any code, read the relevant doc in `docs/modules/`."
- "Before opening a PR: no dead code, no hardcoded values, docstrings on all public symbols, state contract documented, docs updated."
- "Never modify `core/state.py` or `core/interfaces.py` without an approved issue first."
- "Never add a node to `core/graph.py` without a corresponding entry in `docs/architecture.md`."
- "Never add a subagent without a corresponding section in `docs/modules/agents.md`."

---

## 5. Security Requirements

- **No secrets in source.** `.env` is in `.gitignore`. `.env.example` has placeholder values only.
- **No logging of user speech.** Audio bytes and transcribed content are never written to disk or logged at INFO level or above. DEBUG-level transcript logging is permitted but must be documented.
- **No logging of LLM responses** at INFO level by default.
- **API keys always in headers**, never URL parameters.
- **Pinned dependencies.** `requirements.txt` uses exact versions (`==`). Run `pip audit` before any deployment to an untrusted environment.
- **No network calls outside configured endpoints.** External URLs go in `config.yaml` under their tool's namespace. No hardcoded third-party URLs in module code.
- **`audio_bytes` is ephemeral.** Must be `None` in state before leaving the `transcribe` node. Never persisted to `MemorySaver` checkpointer.

---

## 6. Error Handling Standard

Define `RenixError` base exception in `core/utils.py`. Each area defines a subclass: `AudioError`, `WakeWordError`, `TranscriptionError`, `LLMError`, `TTSError`, `ToolError`, `AgentError`, `ConfigError`.

```python
# Correct pattern inside a node
try:
    result = some_call()
except SomeSpecificError as e:
    logger.error("Context description — failed to do X: %s", e, exc_info=True)
    return {"error": f"Readable description: {e}", "response": None}
```

Nodes that fail set `state["error"]` and return. The orchestrator reads `state["error"]` on entry and decides: surface to user, silently retry, or clear and continue. The graph never crashes from a recoverable node failure.

---

## 7. Testing Requirements

- **Unit tests** for: `GraphState` schema, `route` node dispatch logic, tool registry build, agent registry build, device manager fallback.
- **Integration tests** for: full reactive turn with mocked STT/LLM/TTS (verify state transitions and that respond is called with correct text), full proactive turn (verify scheduler sets proactive_message, orchestrator generates response, TTS called).
- Node functions are pure — test them by calling directly with a state dict. No LangGraph runtime needed for unit tests.
- Target 80%+ coverage on `core/` and `modules/tools/registry.py`.
- All tests pass (`pytest`), linting passes (`ruff check .`), type checking passes (`mypy .`) before any PR merges.

---

## 8. v0.1 Build Order

Each step is a separate issue and PR. Build in this exact order.

| Step | Issue title | Deliverable |
|------|-------------|-------------|
| 1 | `feat(repo): scaffold structure` | Directory tree, `__init__.py` files, `pyproject.toml`, `.gitignore`, doc stubs |
| 2 | `feat(config): config loading and validation` | `config.yaml`, `.env.example`, loader in `core/utils.py`, `ConfigError` |
| 3 | `feat(core): state schema` | `core/state.py`, `GraphState` TypedDict, unit tests |
| 4 | `feat(core): interfaces` | `core/interfaces.py` — all abstract base classes |
| 5 | `feat(audio): device autodiscovery` | `device_manager.py`, fallback logic, unit tests |
| 6 | `feat(wake-word): detector` | `modules/wake_word/detector.py` |
| 7 | `feat(stt): transcriber` | `modules/stt/transcriber.py` |
| 8 | `feat(tts): speaker` | `modules/tts/speaker.py` |
| 9 | `feat(tools): registry + builtins` | Registry, time tool, weather tool, unit tests |
| 10 | `feat(agents): tool-use subagent` | `tool_use_agent.py` with internal `ToolNode` loop |
| 11 | `feat(agents): memory subagent` | `memory_agent.py`, SQLite backend |
| 12 | `feat(agents): mcp subagent` | `mcp_agent.py`, MCP proxy tools |
| 13 | `feat(core): graph nodes` | All six nodes: listen, transcribe, route, orchestrator, respond, scheduler |
| 14 | `feat(core): parent graph` | `core/graph.py` — wires nodes + subagents, `MemorySaver` attached |
| 15 | `feat(repo): main.py + startup` | Config load → device discovery → graph compile → listen loop + APScheduler |
| 16 | `docs: full documentation pass` | All module docs, architecture.md with diagrams, all three ADRs complete |
| 17 | `feat(repo): CONTRIBUTING.md + AGENTS.md` | Contributor and agent rules finalized |

---

## 9. Future Expansion Compatibility Check

Before closing v0.1, verify each of the following can be added as a PR without modifying `core/graph.py`, `core/state.py`, or `core/interfaces.py`:

| Capability | How it plugs in |
|---|---|
| New subagent | New `SubagentPlugin` in `modules/agents/`, one line in `AGENTS`, intent label in `route.py` |
| New tool | New `ToolPlugin` in `modules/tools/builtin/`, one line in `TOOLS` |
| MCP server tools | `ToolPlugin` wrappers proxying to MCP endpoints |
| Alternative STT engine | New `Transcriber` implementation + config change |
| Alternative TTS engine | New `Speaker` implementation + config change |
| Alternative wake word | New `WakeWordDetector` implementation + config change |
| Web UI | Module subscribing to graph events via LangGraph streaming API |
| Multi-user sessions | Each session gets its own `thread_id` — zero graph changes |
| Phone calling | Twilio as audio I/O source implementing recorder interface |
| Always-on daemon | `main.py --daemon` flag + systemd unit file — no graph changes |
| System control tools | `ToolPlugin` implementations calling OS APIs or GPIO |

---

## 10. PR Checklist (enforced via PR template)

```markdown
## What does this PR do?
<!-- One sentence. -->

## Related issue
Closes #

## Checklist
- [ ] No dead code or unused imports
- [ ] No hardcoded secrets or configuration values
- [ ] All public functions/classes have docstrings with type hints
- [ ] GraphState not mutated in place — nodes return partial dicts
- [ ] State contract documented for any new or modified node
- [ ] Module or agent doc in docs/modules/ updated
- [ ] docs/architecture.md updated if graph structure changed
- [ ] All tests pass (pytest)
- [ ] Linting passes (ruff check .)
- [ ] Type checking passes (mypy .)
- [ ] Synced with main before this PR was opened (git pull origin main)
- [ ] One issue addressed — no bundled unrelated changes
```

---

*This document is the ground truth. When in doubt, open an issue before deviating.*