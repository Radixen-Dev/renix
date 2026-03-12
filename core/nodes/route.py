"""route node — conditional edge that classifies intent and selects a subagent.

This node is a conditional edge function, not a regular processing node. It
reads ``state["intent"]`` (set by the orchestrator) and returns the name of
the next node to dispatch to. If no subagent is needed the orchestrator
handles the response directly and this node is not called.

State inputs:  intent, active_subagent
State outputs: active_subagent
Edges:         → [agent.name] for each registered SubagentPlugin
               → orchestrator if intent does not match any agent (fallback)

Dispatch table:
    Intent labels map to SubagentPlugin.name values. This table must be
    updated whenever a new subagent is registered in modules/agents/__init__.py.
    See docs/modules/route.md for the full dispatch table.
"""

from __future__ import annotations

from langgraph.types import RunnableConfig

from core.state import GraphState
from core.utils import get_logger

logger = get_logger(__name__)

# Intent → subagent name dispatch table.
# Update this dict when adding a new subagent (step documented in AGENTS.md).
INTENT_DISPATCH: dict[str, str] = {
    "tool_use": "tool_use",
    "memory": "memory",
    "mcp": "mcp",
}


def route(state: GraphState, config: RunnableConfig) -> str:
    """Return the name of the next node based on the classified intent.

    Called as a conditional edge source. Reads ``state["intent"]`` and maps
    it to a registered subagent node name.

    Args:
        state: Current graph state. Reads ``intent``.
        config: LangGraph runnable config.

    Returns:
        Node name string for LangGraph to transition to. Falls back to
        ``"orchestrator"`` if the intent is unknown.
    """
    # Implemented in step 13 — feat(core): graph nodes
    raise NotImplementedError("route node implemented in step 13")


def route_after_orchestrator(state: GraphState) -> str:
    """Conditional edge: decide whether to run a subagent or go straight to respond.

    Args:
        state: Current graph state. Reads ``intent`` and ``response``.

    Returns:
        ``"route"`` if ``intent`` is set (delegate to subagent).
        ``"respond"`` if ``response`` is set (ready to speak).
    """
    # Implemented in step 13 — feat(core): graph nodes
    raise NotImplementedError("route_after_orchestrator implemented in step 13")
