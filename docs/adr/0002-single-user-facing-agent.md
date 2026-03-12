# ADR-0002: Single User-Facing Agent

**Date:** 2026-03-12  
**Status:** Accepted

## Context

Renix includes multiple subagents (tool execution, long-term memory, MCP proxy). An early design considered allowing subagents to speak directly to the user, returning their own TTS output as part of their subgraph execution.

This would create several problems: inconsistent voice and tone across agents, the user experiencing abrupt agent transitions mid-conversation, difficulty enforcing the security rule that raw tool outputs are never read aloud unfiltered, and subagent internals leaking to the user.

## Decision

The orchestrator agent is the **only** entity that generates text the user hears — for both reactive (user speaks) and proactive (Renix initiates) conversations. Subagents run silently in the background, return results into `GraphState` via `messages`, and the orchestrator decides what to say and how. The user never knows subagents exist.

## Consequences

**Easier:**
- Consistent voice, tone, and persona — all user-facing text goes through a single prompt.
- The orchestrator can filter, rephrase, and contextualise tool outputs before speaking.
- Subagents are independently replaceable without affecting the user experience.
- The security boundary is clear: nothing reaches TTS except `state["response"]` set by the orchestrator.

**Harder:**
- The orchestrator node becomes a required pass-through even when a subagent's result is simple. This adds one LLM call per subagent turn.
- The orchestrator's system prompt must be carefully maintained to ensure it knows when and how to synthesise subagent results.
