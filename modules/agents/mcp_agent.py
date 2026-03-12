"""MCP subagent — Model Context Protocol server proxy tools.

Intent labels dispatched here: ``"mcp"``

Proxies tool calls to one or more MCP servers configured in config.yaml
under ``tools.mcp.servers``. Each server's tools are wrapped as ToolPlugin
instances and made available to the LLM via a ToolNode loop (same pattern
as tool_use_agent).
"""

from __future__ import annotations

from langgraph.graph import StateGraph

from core.interfaces import SubagentPlugin
from core.utils import AgentError, get_logger

logger = get_logger(__name__)


class MCPAgent(SubagentPlugin):
    """Subagent that proxies tool calls to configured MCP servers.

    Wraps MCP server endpoints as LangChain tools and runs them through an
    LLM-ToolNode loop, just like ToolUseAgent. Configured via config.yaml.

    Attributes:
        name: ``"mcp"`` — must match the intent label in route.py.
        description: Shown to the orchestrator to explain when to delegate.
    """

    name = "mcp"
    description = (
        "Executes tools provided by connected MCP (Model Context Protocol) "
        "servers. Delegate here when the request requires capabilities exposed "
        "by an external MCP server."
    )

    def build(self) -> StateGraph:
        """Build the MCP subgraph with proxy tool bindings.

        Returns:
            Compiled LangGraph StateGraph for MCP tool execution.

        Raises:
            AgentError: If MCP server configuration is missing or unreachable.
        """
        # Implemented in step 12 — feat(agents): mcp subagent
        raise NotImplementedError("MCPAgent.build implemented in step 12")
