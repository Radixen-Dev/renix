"""Unit tests for the tool registry.

Verifies that:
- build_langchain_tools converts ToolPlugin instances to BaseTool objects.
- Each resulting tool has the correct name and description.
- The TOOLS list contains all expected built-in plugins.
- An empty TOOLS list produces an empty result without errors.

Implemented in step 9 — feat(tools): registry + builtins.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from core.interfaces import ToolPlugin
from core.utils import ToolError
from modules.tools import TOOLS
from modules.tools.builtin.time_tool import TimeTool
from modules.tools.builtin.weather_tool import WeatherTool
from modules.tools.registry import build_langchain_tools


@dataclass
class _EchoTool(ToolPlugin):
    """Simple test plugin that echoes a provided message."""

    name: str
    description: str

    def run(self, **kwargs: object) -> str:
        return str(kwargs.get("message", ""))


class TestBuildLangchainTools:
    """Tests for tools/registry.py conversion logic."""

    def test_empty_plugins_returns_empty_list(self) -> None:
        """build_langchain_tools([]) must return an empty list."""
        assert build_langchain_tools([]) == []

    def test_tool_names_are_preserved(self) -> None:
        """Each resulting BaseTool must have the same name as its ToolPlugin."""
        tools = build_langchain_tools(
            [
                _EchoTool(name="echo_one", description="Echo first"),
                _EchoTool(name="echo_two", description="Echo second"),
            ]
        )
        assert [tool.name for tool in tools] == ["echo_one", "echo_two"]

    def test_tool_descriptions_are_preserved(self) -> None:
        """Each resulting BaseTool must carry the plugin's description."""
        tools = build_langchain_tools(
            [
                _EchoTool(name="echo_desc", description="Useful echo"),
            ]
        )
        assert tools[0].description == "Useful echo"

    def test_duplicate_names_raise_tool_error(self) -> None:
        """Duplicate tool names must be rejected by the registry."""
        with pytest.raises(ToolError, match="Duplicate tool name"):
            build_langchain_tools(
                [
                    _EchoTool(name="dup", description="A"),
                    _EchoTool(name="dup", description="B"),
                ]
            )


class TestBuiltinTools:
    """Tests for TimeTool and WeatherTool plugins."""

    def test_time_tool_name(self) -> None:
        """TimeTool.name must be 'get_current_time'."""
        assert TimeTool.name == "get_current_time"
        assert TimeTool().run() != ""

    def test_weather_tool_name(self) -> None:
        """WeatherTool.name must be 'get_weather'."""
        assert WeatherTool.name == "get_weather"

    def test_tools_registry_contains_expected_builtins(self) -> None:
        """TOOLS registry should include time and weather plugin instances."""
        names = {tool.name for tool in TOOLS}
        assert "get_current_time" in names
        assert "get_weather" in names

    def test_weather_tool_requires_location(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """WeatherTool should reject missing location argument."""
        monkeypatch.setenv("WEATHER_API_KEY", "dummy")
        weather_tool = WeatherTool()

        with pytest.raises(ToolError, match="requires a non-empty 'location'"):
            weather_tool.run()

    def test_weather_tool_success_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """WeatherTool should return a formatted weather summary."""
        monkeypatch.setenv("WEATHER_API_KEY", "dummy")
        weather_tool = WeatherTool()
        monkeypatch.setattr(
            weather_tool,
            "_resolve_base_url",
            lambda: "https://api.example.com",
        )
        monkeypatch.setattr(
            weather_tool,
            "_fetch_json",
            lambda _url: {
                "name": "London",
                "main": {"temp": 12.4},
                "weather": [{"description": "partly cloudy"}],
                "wind": {"speed": 5.3},
            },
        )

        result = weather_tool.run(location="London")

        assert "London" in result
        assert "12" in result
        assert "partly cloudy" in result
