"""Unit tests for the tool registry.

Verifies that:
- build_langchain_tools converts ToolPlugin instances to BaseTool objects.
- Each resulting tool has the correct name and description.
- The TOOLS list contains all expected built-in plugins.
- An empty TOOLS list produces an empty result without errors.

Implemented in step 9 — feat(tools): registry + builtins.
"""

from __future__ import annotations

import pytest


class TestBuildLangchainTools:
    """Tests for tools/registry.py conversion logic."""

    def test_empty_plugins_returns_empty_list(self) -> None:
        """build_langchain_tools([]) must return an empty list."""
        pytest.skip("Implemented in step 9 — feat(tools): registry + builtins")

    def test_tool_names_are_preserved(self) -> None:
        """Each resulting BaseTool must have the same name as its ToolPlugin."""
        pytest.skip("Implemented in step 9 — feat(tools): registry + builtins")

    def test_tool_descriptions_are_preserved(self) -> None:
        """Each resulting BaseTool must carry the plugin's description."""
        pytest.skip("Implemented in step 9 — feat(tools): registry + builtins")


class TestBuiltinTools:
    """Tests for TimeTool and WeatherTool plugins."""

    def test_time_tool_name(self) -> None:
        """TimeTool.name must be 'get_current_time'."""
        pytest.skip("Implemented in step 9 — feat(tools): registry + builtins")

    def test_weather_tool_name(self) -> None:
        """WeatherTool.name must be 'get_weather'."""
        pytest.skip("Implemented in step 9 — feat(tools): registry + builtins")
