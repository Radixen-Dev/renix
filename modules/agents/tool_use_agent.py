"""Tool-use subagent — multi-step tool execution via LangGraph ToolNode.

Intent labels dispatched here: ``"tool_use"``

Internal subgraph topology:
    llm_call → tools (ToolNode) → llm_call  [loop until no tool calls]
             ↘ END (when LLM produces a final answer)

All registered TOOLS from modules/tools/__init__.py are bound to the ToolNode.
"""

from __future__ import annotations

from langgraph.graph import StateGraph

from core.interfaces import SubagentPlugin
from core.utils import get_logger

logger = get_logger(__name__)


class ToolUseAgent(SubagentPlugin):
    """Subagent that executes multi-step tool chains.

    Uses a LangGraph ``ToolNode`` loop: the LLM calls tools repeatedly until
    it produces a final text answer, which is written back to the parent
    ``GraphState`` via ``messages``.

    Attributes:
        name: ``"tool_use"`` — must match the intent label in route.py.
        description: Shown to the orchestrator to explain when to delegate.
    """

    name = "tool_use"
    description = (
        "Executes one or more tool calls (e.g. look up the time, weather, or "
        "perform calculations) and returns the result. Delegate here when the "
        "request requires calling an external tool."
    )

    def build(self) -> StateGraph:
        """Build the tool-use subgraph with an LLM-ToolNode loop.

        Returns:
            Compiled LangGraph StateGraph implementing the tool-call loop.

        Raises:
            AgentError: If required tools or LLM config are unavailable.
        """
        # Implemented in step 10 — feat(agents): tool-use subagent
        raise NotImplementedError("ToolUseAgent.build implemented in step 10")
