"""Unit tests for the MCP subagent proxy tool discovery and graph behavior."""

from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any

import pytest
from langchain_core.messages import HumanMessage

from modules.agents.mcp_agent import (
    MCPAgent,
    _fetch_tool_manifest,
    _invoke_mcp_tool,
    _make_proxy_tool,
    _mcp_disabled_node,
    _url_slug,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _base_state(messages: list[object]) -> dict[str, object]:
    """Build a minimal GraphState payload for subagent invocation tests."""
    return {
        "messages": messages,
        "transcript": None,
        "response": None,
        "intent": None,
        "active_subagent": None,
        "audio_bytes": None,
        "proactive_message": None,
        "error": None,
    }


def _agent_no_servers() -> MCPAgent:
    """Return an MCPAgent wired to an empty server list."""
    agent = MCPAgent()
    agent._load_cfg = lambda: {  # type: ignore[assignment]
        "llm": {
            "base_url": "http://localhost:1234/v1",
            "model": "test-model",
            "temperature": 0.0,
        },
        "tools": {"mcp": {"servers": []}},
    }
    return agent


# ---------------------------------------------------------------------------
# _url_slug
# ---------------------------------------------------------------------------


class TestUrlSlug:
    """Tests for the URL → identifier slug helper."""

    def test_simple_host(self) -> None:
        """Hostname should be converted to an underscore slug."""
        assert _url_slug("http://localhost:8080") == "localhost_8080"

    def test_path_included(self) -> None:
        """Path segments should appear in the slug."""
        slug = _url_slug("http://myserver.example.com/mcp/v1")
        assert "myserver" in slug
        assert "example" in slug

    def test_fallback_for_empty(self) -> None:
        """An unparseable URL should fall back to 'mcp'."""
        assert _url_slug("") == "mcp"


# ---------------------------------------------------------------------------
# _mcp_disabled_node
# ---------------------------------------------------------------------------


class TestMcpDisabledNode:
    """Tests for the no-servers disabled notice node."""

    def test_returns_notice_message(self) -> None:
        """Disabled node should append a human-readable AIMessage."""
        result = _mcp_disabled_node(_base_state([]))  # type: ignore[arg-type]
        messages = result.get("messages", [])
        assert messages
        content = str(messages[-1].content)
        assert "No MCP servers" in content


# ---------------------------------------------------------------------------
# _fetch_tool_manifest (with a real local HTTP server)
# ---------------------------------------------------------------------------


class _ManifestServer(BaseHTTPRequestHandler):
    """Minimal HTTP server returning a canned tool manifest."""

    tools_payload: bytes = b"[]"

    def do_GET(self) -> None:  # noqa: N802
        """Respond to GET /tools with the canned payload."""
        if self.path == "/tools":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(self.tools_payload)
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args: Any) -> None:  # noqa: D102
        """Suppress HTTP server output during tests."""


def _start_manifest_server(payload: bytes) -> tuple[HTTPServer, int]:
    """Start a one-shot HTTP server on a free port and return (server, port)."""
    _ManifestServer.tools_payload = payload
    server = HTTPServer(("127.0.0.1", 0), _ManifestServer)
    port = server.server_address[1]
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, port


class TestFetchToolManifest:
    """Tests for the HTTP-based MCP tool discovery."""

    def test_returns_empty_list(self) -> None:
        """Server returning [] should yield an empty manifest list."""
        server, port = _start_manifest_server(b"[]")
        try:
            result = _fetch_tool_manifest(f"http://127.0.0.1:{port}")
        finally:
            server.shutdown()
        assert result == []

    def test_returns_tool_entries(self) -> None:
        """Server returning tool objects should be parsed correctly."""
        payload = json.dumps(
            [{"name": "say_hello", "description": "Greets the user."}]
        ).encode()
        server, port = _start_manifest_server(payload)
        try:
            result = _fetch_tool_manifest(f"http://127.0.0.1:{port}")
        finally:
            server.shutdown()
        assert len(result) == 1
        assert result[0]["name"] == "say_hello"

    def test_raises_on_unreachable_server(self) -> None:
        """Unreachable server should raise AgentError."""
        from core.utils import AgentError

        with pytest.raises(AgentError):
            _fetch_tool_manifest("http://127.0.0.1:1")  # port 1 should be unreachable


# ---------------------------------------------------------------------------
# _invoke_mcp_tool (with a real local HTTP server)
# ---------------------------------------------------------------------------


class _InvokeServer(BaseHTTPRequestHandler):
    """Minimal HTTP server handling POST /tools/<name>."""

    response_payload: bytes = b'{"result": "ok"}'

    def do_POST(self) -> None:  # noqa: N802
        """Echo back the canned response payload."""
        content_length = int(self.headers.get("Content-Length", 0))
        _ = self.rfile.read(content_length)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(self.response_payload)

    def log_message(self, *args: Any) -> None:  # noqa: D102
        """Suppress HTTP server output during tests."""


def _start_invoke_server(payload: bytes) -> tuple[HTTPServer, int]:
    """Start a POST-handling server on a free port."""
    _InvokeServer.response_payload = payload
    server = HTTPServer(("127.0.0.1", 0), _InvokeServer)
    port = server.server_address[1]
    Thread(target=server.serve_forever, daemon=True).start()
    return server, port


class TestInvokeMcpTool:
    """Tests for the HTTP-based MCP tool invocation."""

    def test_returns_result_field(self) -> None:
        """Server returning {result: '...'} should return that string."""
        server, port = _start_invoke_server(b'{"result": "hello world"}')
        try:
            result = _invoke_mcp_tool(
                f"http://127.0.0.1:{port}", "say_hello", {"name": "Alice"}
            )
        finally:
            server.shutdown()
        assert result == "hello world"

    def test_returns_output_field_fallback(self) -> None:
        """Server returning {output: '...'} should fall back to that field."""
        server, port = _start_invoke_server(b'{"output": "fallback result"}')
        try:
            result = _invoke_mcp_tool(
                f"http://127.0.0.1:{port}", "tool", {}
            )
        finally:
            server.shutdown()
        assert result == "fallback result"

    def test_raises_on_unreachable_server(self) -> None:
        """Unreachable server should raise AgentError."""
        from core.utils import AgentError

        with pytest.raises(AgentError):
            _invoke_mcp_tool("http://127.0.0.1:1", "tool", {})


# ---------------------------------------------------------------------------
# _make_proxy_tool
# ---------------------------------------------------------------------------


class TestMakeProxyTool:
    """Tests for the proxy tool factory."""

    def test_tool_name_and_description(self) -> None:
        """Proxy tool should carry the name and description provided."""
        tool = _make_proxy_tool(
            tool_name="srv__greet",
            description="Greets the user.",
            server_url="http://localhost:8080",
            remote_tool_name="greet",
        )
        assert tool.name == "srv__greet"
        assert "Greets" in tool.description


# ---------------------------------------------------------------------------
# MCPAgent.build — no-servers path
# ---------------------------------------------------------------------------


class TestMCPAgentNoServers:
    """Tests for MCPAgent when no MCP servers are configured."""

    def test_build_returns_compiled_graph(self) -> None:
        """build() should return a compiled graph even with no servers."""
        agent = _agent_no_servers()
        compiled = agent.build()
        assert hasattr(compiled, "invoke")

    def test_invoke_returns_disabled_notice(self) -> None:
        """Invoking the graph with no servers should return a notice message."""
        agent = _agent_no_servers()
        compiled = agent.build()
        result = compiled.invoke(_base_state([HumanMessage(content="use mcp")]))
        messages = result.get("messages", [])
        assert messages
        assert "No MCP servers" in str(messages[-1].content)


# ---------------------------------------------------------------------------
# MCPAgent.build — with servers (mocked HTTP discovery + LLM)
# ---------------------------------------------------------------------------


class TestMCPAgentWithServers:
    """Tests for MCPAgent with mocked MCP server discovery."""

    def test_build_with_tools_returns_compiled_graph(self) -> None:
        """build() should compile successfully when a server provides tools."""
        tool_manifest = [{"name": "ping", "description": "Pings the server."}]
        server, port = _start_manifest_server(
            json.dumps(tool_manifest).encode()
        )
        base_url = f"http://127.0.0.1:{port}"

        try:
            agent = MCPAgent()
            agent._load_cfg = lambda: {  # type: ignore[assignment]
                "llm": {
                    "base_url": "http://localhost:1234/v1",
                    "model": "test-model",
                    "temperature": 0.0,
                },
                "tools": {"mcp": {"servers": [base_url]}},
            }

            # langchain-openai may not be installed in CI — tolerate AgentError.
            from core.utils import AgentError

            try:
                compiled = agent.build()
                assert hasattr(compiled, "invoke")
            except AgentError as exc:
                assert "langchain-openai" in str(exc) or "initialise" in str(exc)
        finally:
            server.shutdown()

    def test_unreachable_server_falls_back_to_disabled(self) -> None:
        """When the only configured server is unreachable, build disabled graph."""
        agent = MCPAgent()
        agent._load_cfg = lambda: {  # type: ignore[assignment]
            "llm": {
                "base_url": "http://localhost:1234/v1",
                "model": "test-model",
                "temperature": 0.0,
            },
            "tools": {"mcp": {"servers": ["http://127.0.0.1:1"]}},
        }
        # Should not raise — falls back to mcp_disabled subgraph.
        compiled = agent.build()
        assert hasattr(compiled, "invoke")
        result = compiled.invoke(_base_state([HumanMessage(content="mcp task")]))
        assert "No MCP servers" in str(result["messages"][-1].content)
