"""Tool-use subagent — multi-step tool execution via LangGraph ToolNode.

Intent labels dispatched here: ``"tool_use"``

Internal subgraph topology:
    llm_call → tools (ToolNode) → llm_call  [loop until no tool calls]
             ↘ END (when LLM produces a final answer)

All registered TOOLS from modules/tools/__init__.py are bound to the ToolNode.
"""

from __future__ import annotations

import os
from typing import Any, cast

from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from core.interfaces import SubagentPlugin
from core.state import GraphState
from core.utils import AgentError, get_config, get_logger, load_config
from modules.tools import TOOLS
from modules.tools.registry import build_langchain_tools

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
        tools = build_langchain_tools(TOOLS)
        if not tools:
            raise AgentError("ToolUseAgent requires at least one registered tool.")

        cfg = self._load_cfg()
        llm_cfg = cfg.get("llm")
        if not isinstance(llm_cfg, dict):
            raise AgentError("Missing 'llm' section in config.")

        base_url = llm_cfg.get("base_url")
        model = llm_cfg.get("model")
        if not isinstance(base_url, str) or not base_url.strip():
            raise AgentError("ToolUseAgent requires llm.base_url in config.")
        if not isinstance(model, str) or not model.strip():
            raise AgentError("ToolUseAgent requires llm.model in config.")

        api_key = os.getenv("LLM_API_KEY", "local-dev-key")

        try:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                base_url=base_url,
                model=model,
                api_key=api_key,
                temperature=float(llm_cfg.get("temperature", 0.0) or 0.0),
            )
            llm_with_tools = llm.bind_tools(tools)
            tool_node = ToolNode(tools)
        except ImportError as exc:
            raise AgentError(
                "langchain-openai is not installed. "
                "Install requirements.txt dependencies."
            ) from exc
        except Exception as exc:
            raise AgentError(f"Failed to initialize ToolUseAgent: {exc}") from exc

        graph = StateGraph(GraphState)
        graph.add_node("llm_call", lambda state: self._llm_call(state, llm_with_tools))
        graph.add_node("tools", tool_node)
        graph.add_edge(START, "llm_call")
        graph.add_conditional_edges(
            "llm_call",
            self._route_after_llm,
            {
                "tools": "tools",
                "end": END,
            },
        )
        graph.add_edge("tools", "llm_call")

        return cast(StateGraph, graph.compile())

    def _llm_call(self, state: GraphState, llm_with_tools: Any) -> dict[str, Any]:
        """Invoke the tool-enabled LLM and append the new AI message."""
        messages = state.get("messages", [])
        if not isinstance(messages, list):
            raise AgentError("ToolUseAgent requires state['messages'] to be a list.")

        try:
            response = llm_with_tools.invoke(messages)
        except Exception as exc:
            raise AgentError(f"Tool-use LLM invocation failed: {exc}") from exc

        return {"messages": [response]}

    def _route_after_llm(self, state: GraphState) -> str:
        """Route to tools when the latest AI message contains tool calls."""
        messages = state.get("messages", [])
        if not isinstance(messages, list) or not messages:
            return "end"

        last = messages[-1]
        tool_calls = getattr(last, "tool_calls", None)
        if isinstance(tool_calls, list) and tool_calls:
            return "tools"
        return "end"

    def _load_cfg(self) -> dict[str, Any]:
        """Return loaded config, loading from disk if needed."""
        try:
            return get_config()
        except Exception:
            return load_config()
