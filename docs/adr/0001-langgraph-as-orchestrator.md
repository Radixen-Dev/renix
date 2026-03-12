# ADR-0001: LangGraph as Orchestrator

**Date:** 2026-03-12  
**Status:** Accepted

## Context

Renix requires a turn-based conversation loop with conditional routing, subagent dispatch, stateful memory, and support for both reactive (user-triggered) and proactive (timer-triggered) conversation entry points.

Before LangGraph, the design considered a custom event bus with a hand-rolled orchestration loop. This approach would require maintaining graph topology in imperative code, implementing state merging manually, writing custom checkpointing for turn-to-turn memory, and handling concurrent entry points (reactive vs. proactive) without a standard abstraction.

## Decision

Use LangGraph as the sole orchestrator. The compiled `StateGraph` owns the full turn lifecycle. There is no custom event bus, no hand-rolled loop. Graph edges are control flow; `GraphState` is the single source of truth per turn. `MemorySaver` provides turn-to-turn memory at zero implementation cost.

## Consequences

**Easier:**
- Adding new routing logic requires only a new conditional edge function.
- Subagents are compiled subgraphs — standard LangGraph composition.
- Turn-to-turn memory is handled by the checkpointer, not application code.
- The graph is inspectable and visualisable via LangGraph's built-in tools.
- Streaming, interrupts, and human-in-the-loop are available without custom code.

**Harder:**
- The LangGraph API is a required dependency — the orchestration layer is not portable to other frameworks without a rewrite.
- Contributors must understand LangGraph's node/edge/state model before contributing to `core/`.
