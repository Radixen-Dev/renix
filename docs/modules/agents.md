# agents.md — Subagent Plugin System

> **Status:** Stub — to be completed in step 16 (`docs: full documentation pass`).

---

## Overview

Subagents are self-contained compiled LangGraph subgraphs registered in `modules/agents/__init__.py`. Each implements `SubagentPlugin` from `core/interfaces.py`. The parent graph registers each subgraph as a node at startup.

The user never interacts with subagents directly. They run silently, return results into `state["messages"]`, and the orchestrator synthesises the response.

---

## How to Add a Subagent

1. Create `modules/agents/my_agent.py` implementing `SubagentPlugin`.
2. Add an instance to `AGENTS` in `modules/agents/__init__.py`.
3. Add the intent label(s) to `INTENT_DISPATCH` in `core/nodes/route.py`.
4. Add a section to this file with: purpose, intent labels, subgraph topology diagram, tools bound, state contract, how to extend.

**No other files change.**

---

## ToolUseAgent

- **Intent labels:** `tool_use`
- **Purpose:** Executes multi-step tool chains using a LangGraph `ToolNode` loop.
- **Tools bound:** All `TOOLS` from `modules/tools/__init__.py`.
- **State contract:**
  - Reads: `messages`
  - Writes: `messages` (appended with tool calls and results)

### Step 10 Verification

- `ToolUseAgent` now implements a working internal ToolNode loop in `modules/agents/tool_use_agent.py`:
  - builds LangChain tools from `modules/tools/__init__.py`
  - initializes tool-capable ChatOpenAI client from `config.yaml` (`llm.base_url`, `llm.model`)
  - runs loop topology: `llm_call -> tools -> llm_call` until no tool calls remain
  - returns a compiled subgraph for parent-graph registration in step 14
- Unit coverage in `tests/unit/test_agent_registry.py` now verifies:
  - AGENTS registry is non-empty and unique by name
  - all registered entries implement `SubagentPlugin`
  - `ToolUseAgent.build()` returns a compiled graph object

<!-- TODO (step 16): Add Mermaid subgraph topology diagram. -->

---

## MemoryAgent

- **Intent labels:** `memory`
- **Purpose:** Cross-session long-term memory recall and storage via SQLite.
- **Tools bound:** Internal memory read/write tools (not in global TOOLS).
- **State contract:**
  - Reads: `messages`
  - Writes: `messages` (appended with memory recall results)

### Step 11 Verification

- `MemoryAgent` now implements a SQLite-backed long-term memory subgraph in `modules/agents/memory_agent.py`:
  - loads memory config from `config.yaml` (`memory.long_term_enabled`, `memory.db_path`)
  - initializes SQLite schema (`memories` table) automatically
  - executes `classify -> store|recall -> END` flow
  - persists memory text on store requests and returns recall summaries on query requests
  - supports explicit disabled mode response when long-term memory is turned off
- Unit coverage in `tests/unit/test_memory_agent.py` verifies:
  - SQLite add/search roundtrip behavior
  - end-to-end store-then-recall graph behavior
  - disabled-memory branch behavior

<!-- TODO (step 16): Add Mermaid subgraph topology diagram. -->

---

## MCPAgent

- **Intent labels:** `mcp`
- **Purpose:** Proxies tool calls to configured MCP servers.
- **Tools bound:** Dynamically loaded from MCP server manifests at startup via `GET {server_url}/tools`.
- **State contract:**
  - Reads: `messages`
  - Writes: `messages` (appended with MCP tool results)

### Step 12 Verification

- `MCPAgent` implements a full MCP proxy subgraph in `modules/agents/mcp_agent.py`:
  - reads server URLs from `config.yaml` (`tools.mcp.servers`)
  - discovers tools at startup via `GET {server_url}/tools` (JSON array of `{name, description}`)
  - invokes tools via `POST {server_url}/tools/{tool_name}` with kwargs as JSON body
  - wraps each discovered tool as a LangChain `StructuredTool` using `_make_proxy_tool`
  - qualifies tool names as `{server_slug}__{tool_name}` to avoid collisions across servers
  - runs the same LLM-ToolNode loop as `ToolUseAgent`: `llm_call → tools → llm_call` until no tool calls remain
  - falls back to a `mcp_disabled` single-node subgraph (graceful notice) when no servers are configured or all servers are unreachable at build time
  - uses only stdlib `urllib` — no additional runtime dependencies
- Unit coverage in `tests/unit/test_mcp_agent.py` verifies:
  - `_url_slug` slug generation
  - `_mcp_disabled_node` notice content
  - `_fetch_tool_manifest` via real local HTTP server (empty list, tool entries, unreachable)
  - `_invoke_mcp_tool` via real local HTTP server (`result`, `output` field fallbacks, unreachable)
  - `_make_proxy_tool` name and description propagation
  - `MCPAgent.build()` no-servers path returns a compiled graph and invokes the disabled notice
  - `MCPAgent.build()` unreachable-server path falls back gracefully to disabled subgraph
  - `MCPAgent.build()` with mocked manifest returns a compiled graph (or raises `AgentError` when `langchain-openai` is absent)

<!-- TODO (step 16): Add Mermaid subgraph topology diagram. -->
