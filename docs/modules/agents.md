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

<!-- TODO (step 16): Add Mermaid subgraph topology diagram. -->

---

## MemoryAgent

- **Intent labels:** `memory`
- **Purpose:** Cross-session long-term memory recall and storage via SQLite.
- **Tools bound:** Internal memory read/write tools (not in global TOOLS).
- **State contract:**
  - Reads: `messages`
  - Writes: `messages` (appended with memory recall results)

<!-- TODO (step 16): Add Mermaid subgraph topology diagram. -->

---

## MCPAgent

- **Intent labels:** `mcp`
- **Purpose:** Proxies tool calls to configured MCP servers.
- **Tools bound:** Dynamically loaded from MCP server manifests at startup.
- **State contract:**
  - Reads: `messages`
  - Writes: `messages` (appended with MCP tool results)

<!-- TODO (step 16): Add Mermaid subgraph topology diagram. -->
