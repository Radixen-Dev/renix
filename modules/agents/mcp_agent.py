"""MCP subagent — Model Context Protocol server proxy tools.

Intent labels dispatched here: ``"mcp"``

Proxies tool calls to one or more MCP servers configured in config.yaml
under ``tools.mcp.servers``. Each server's tools are discovered at startup via
``GET {server_url}/tools`` and wrapped as LangChain ``StructuredTool`` objects.
Invocations are forwarded via ``POST {server_url}/tools/{tool_name}``.

If no MCP servers are configured the subgraph returns a graceful notice
without raising an error, so the parent graph continues to function.

Subgraph topology (servers present):
    llm_call → tools (ToolNode) → llm_call  [loop until no tool calls remain]
             ↘ END (when LLM produces a final answer)

Subgraph topology (no servers / disabled):
    mcp_disabled → END
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, cast

from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool, StructuredTool
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from core.interfaces import SubagentPlugin
from core.state import GraphState
from core.utils import AgentError, get_config, get_logger, load_config

logger = get_logger(__name__)

# Maximum seconds to wait for any single MCP HTTP request.
_REQUEST_TIMEOUT = 10


class MCPAgent(SubagentPlugin):
    """Subagent that proxies tool calls to configured MCP servers.

    Discovers tools from every MCP server listed in ``tools.mcp.servers``
    (config.yaml) at startup, wraps them as LangChain tools, and executes
    requests through a ToolNode loop identical to ``ToolUseAgent``.

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

        Discovers tools from all configured MCP servers. When no servers are
        configured, builds a single-node disabled-notice subgraph instead.

        Returns:
            Compiled LangGraph ``StateGraph`` for MCP tool execution.

        Raises:
            AgentError: If LLM configuration is missing when servers are present.
        """
        cfg = self._load_cfg()
        server_urls = self._load_server_urls(cfg)

        graph = StateGraph(GraphState)

        if not server_urls:
            logger.info(
                "MCPAgent: no MCP servers configured — building disabled subgraph."
            )
            graph.add_node("mcp_disabled", _mcp_disabled_node)
            graph.add_edge(START, "mcp_disabled")
            graph.add_edge("mcp_disabled", END)
            return cast(StateGraph, graph.compile())

        tools = self._discover_tools(server_urls)
        if not tools:
            logger.warning(
                "MCPAgent: MCP servers returned no tools — building disabled subgraph."
            )
            graph.add_node("mcp_disabled", _mcp_disabled_node)
            graph.add_edge(START, "mcp_disabled")
            graph.add_edge("mcp_disabled", END)
            return cast(StateGraph, graph.compile())

        llm_cfg = cfg.get("llm")
        if not isinstance(llm_cfg, dict):
            raise AgentError("MCPAgent requires 'llm' section in config.")

        base_url = llm_cfg.get("base_url")
        model = llm_cfg.get("model")
        if not isinstance(base_url, str) or not base_url.strip():
            raise AgentError("MCPAgent requires llm.base_url in config.")
        if not isinstance(model, str) or not model.strip():
            raise AgentError("MCPAgent requires llm.model in config.")

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
            raise AgentError(f"Failed to initialise MCPAgent: {exc}") from exc

        graph.add_node("llm_call", lambda state: _llm_call(state, llm_with_tools))
        graph.add_node("tools", tool_node)
        graph.add_edge(START, "llm_call")
        graph.add_conditional_edges(
            "llm_call",
            _route_after_llm,
            {
                "tools": "tools",
                "end": END,
            },
        )
        graph.add_edge("tools", "llm_call")
        return cast(StateGraph, graph.compile())

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_server_urls(self, cfg: dict[str, Any]) -> list[str]:
        """Extract and validate MCP server URL list from config.

        Args:
            cfg: Loaded configuration dict.

        Returns:
            List of non-empty server URL strings (may be empty).
        """
        tools_cfg = cfg.get("tools")
        if not isinstance(tools_cfg, dict):
            return []
        mcp_cfg = tools_cfg.get("mcp")
        if not isinstance(mcp_cfg, dict):
            return []
        servers = mcp_cfg.get("servers", [])
        if not isinstance(servers, list):
            return []
        return [str(s).rstrip("/") for s in servers if s and str(s).strip()]

    def _discover_tools(self, server_urls: list[str]) -> list[BaseTool]:
        """Contact each MCP server and build LangChain tools from manifests.

        Performs ``GET {server_url}/tools`` for each server. Tools that fail
        discovery are skipped with a warning rather than aborting startup.

        Args:
            server_urls: Validated list of MCP server base URLs.

        Returns:
            List of LangChain ``BaseTool`` objects ready for a ``ToolNode``.
        """
        tools: list[BaseTool] = []
        seen_names: set[str] = set()

        for base_url in server_urls:
            try:
                manifests = _fetch_tool_manifest(base_url)
            except Exception as exc:
                logger.warning(
                    "MCPAgent: could not reach MCP server '%s': %s — skipping.",
                    base_url,
                    exc,
                )
                continue

            for manifest in manifests:
                tool_name = manifest.get("name", "")
                tool_desc = manifest.get("description", "")
                if not tool_name or not isinstance(tool_name, str):
                    logger.warning(
                        "MCPAgent: skipping tool with empty name from '%s'.", base_url
                    )
                    continue
                qualified_name = f"{_url_slug(base_url)}__{tool_name}"
                if qualified_name in seen_names:
                    logger.warning(
                        "MCPAgent: duplicate tool name '%s' from '%s' — skipping.",
                        qualified_name,
                        base_url,
                    )
                    continue
                seen_names.add(qualified_name)
                tools.append(
                    _make_proxy_tool(
                        tool_name=qualified_name,
                        description=(
                            str(tool_desc)
                            if tool_desc
                            else f"MCP tool: {tool_name}"
                        ),
                        server_url=base_url,
                        remote_tool_name=tool_name,
                    )
                )
                logger.info(
                    "MCPAgent: registered tool '%s' from '%s'.",
                    qualified_name,
                    base_url,
                )

        return tools

    def _load_cfg(self) -> dict[str, Any]:
        """Return loaded config, loading from disk if needed."""
        try:
            return get_config()
        except Exception:
            return load_config()


# ---------------------------------------------------------------------------
# Module-level helpers (no self — avoids lambda capture issues)
# ---------------------------------------------------------------------------


def _mcp_disabled_node(state: GraphState) -> dict[str, Any]:
    """Return a notice when no MCP servers are configured or reachable.

    Args:
        state: Current graph state (unused).

    Returns:
        Partial state dict appending an AI notice message.
    """
    _ = state
    return {
        "messages": [
            AIMessage(
                content=(
                    "No MCP servers are currently configured or reachable. "
                    "Add server URLs to tools.mcp.servers in config.yaml."
                )
            )
        ]
    }


def _llm_call(state: GraphState, llm_with_tools: Any) -> dict[str, Any]:
    """Invoke the tool-enabled LLM and append the new AI message.

    Args:
        state: Current graph state.
        llm_with_tools: LangChain LLM with bound tools.

    Returns:
        Partial state dict with the new AI message appended.

    Raises:
        AgentError: If the LLM invocation fails.
    """
    messages = state.get("messages", [])
    if not isinstance(messages, list):
        raise AgentError("MCPAgent requires state['messages'] to be a list.")
    try:
        response = llm_with_tools.invoke(messages)
    except Exception as exc:
        raise AgentError(f"MCP LLM invocation failed: {exc}") from exc
    return {"messages": [response]}


def _route_after_llm(state: GraphState) -> str:
    """Route to tools when the latest AI message contains tool calls.

    Args:
        state: Current graph state.

    Returns:
        ``"tools"`` if tool calls are present, ``"end"`` otherwise.
    """
    messages = state.get("messages", [])
    if not isinstance(messages, list) or not messages:
        return "end"
    last = messages[-1]
    tool_calls = getattr(last, "tool_calls", None)
    if isinstance(tool_calls, list) and tool_calls:
        return "tools"
    return "end"


def _fetch_tool_manifest(base_url: str) -> list[dict[str, Any]]:
    """Fetch the tool list from an MCP server.

    Sends ``GET {base_url}/tools`` and expects a JSON array where each element
    has at minimum a ``name`` key and optionally a ``description`` key.

    Args:
        base_url: MCP server base URL (trailing slash already stripped).

    Returns:
        List of tool manifest dicts from the server.

    Raises:
        AgentError: If the request fails or the response is malformed.
    """
    url = f"{base_url}/tools"
    try:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=_REQUEST_TIMEOUT) as resp:  # noqa: S310
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        raise AgentError(f"MCP server returned HTTP {exc.code} for {url}") from exc
    except urllib.error.URLError as exc:
        raise AgentError(f"MCP server unreachable at {url}: {exc.reason}") from exc
    except Exception as exc:
        raise AgentError(f"MCP tool discovery failed for {url}: {exc}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentError(
            f"MCP server {url} returned non-JSON response: {exc}"
        ) from exc

    if not isinstance(data, list):
        raise AgentError(
            f"MCP server {url} /tools must return a JSON array, "
            f"got {type(data).__name__}."
        )
    return data


def _invoke_mcp_tool(
    server_url: str, remote_tool_name: str, kwargs: dict[str, Any]
) -> str:
    """Call a tool on an MCP server via HTTP POST.

    Sends ``POST {server_url}/tools/{remote_tool_name}`` with ``kwargs``
    serialised as JSON. Expects a JSON object with a ``result`` key.

    Args:
        server_url: MCP server base URL.
        remote_tool_name: Name of the tool as reported by the server.
        kwargs: Tool input parameters.

    Returns:
        Plain string result from the tool.

    Raises:
        AgentError: If the request fails or the response is malformed.
    """
    url = f"{server_url}/tools/{urllib.parse.quote(remote_tool_name, safe='')}"
    payload = json.dumps(kwargs).encode("utf-8")
    try:
        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=_REQUEST_TIMEOUT) as resp:  # noqa: S310
            raw = resp.read()
    except urllib.error.HTTPError as exc:
        raise AgentError(
            f"MCP tool '{remote_tool_name}' returned HTTP {exc.code}"
        ) from exc
    except urllib.error.URLError as exc:
        raise AgentError(
            f"MCP server unreachable while calling '{remote_tool_name}': {exc.reason}"
        ) from exc
    except Exception as exc:
        raise AgentError(
            f"MCP tool '{remote_tool_name}' invocation failed: {exc}"
        ) from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentError(
            f"MCP tool '{remote_tool_name}' returned non-JSON response: {exc}"
        ) from exc

    if isinstance(data, dict):
        result = data.get("result", data.get("output", data.get("content")))
        if result is not None:
            return str(result)
        # Fallback: serialise the whole dict if no recognised key
        return json.dumps(data)

    return str(data)


def _make_proxy_tool(
    tool_name: str,
    description: str,
    server_url: str,
    remote_tool_name: str,
) -> BaseTool:
    """Create a LangChain tool that proxies calls to an MCP server endpoint.

    Args:
        tool_name: Qualified name used by the LangChain ToolNode.
        description: Human-readable description for the LLM tool schema.
        server_url: MCP server base URL.
        remote_tool_name: Name as reported by the MCP server's /tools manifest.

    Returns:
        A LangChain ``StructuredTool`` that forwards calls to the MCP server.
    """
    _surl = server_url
    _rname = remote_tool_name

    def _proxy(**kwargs: Any) -> str:
        return _invoke_mcp_tool(_surl, _rname, kwargs)

    return StructuredTool.from_function(
        func=_proxy,
        name=tool_name,
        description=description,
    )


def _url_slug(url: str) -> str:
    """Derive a safe identifier prefix from a server URL.

    Args:
        url: MCP server base URL.

    Returns:
        Alphanumeric-and-underscore slug derived from the URL hostname/path.
    """
    parsed = urllib.parse.urlparse(url)
    raw = (
        (parsed.netloc + parsed.path)
        .replace(".", "_")
        .replace("/", "_")
        .replace("-", "_")
        .replace(":", "_")
    )
    # Strip leading/trailing underscores and collapse consecutive underscores.
    slug = "_".join(part for part in raw.split("_") if part)
    return slug or "mcp"
