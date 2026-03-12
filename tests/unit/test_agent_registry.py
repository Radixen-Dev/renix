"""Unit tests for the agent registry.

Verifies that:
- AGENTS list contains all expected SubagentPlugin instances.
- Each registered agent has a unique, non-empty name.
- Each agent's name matches the intent labels in INTENT_DISPATCH.
- build() is callable and raises NotImplementedError (stub phase) or returns
  a compiled StateGraph (implementation phase).

Implemented in step 10–12 — feat(agents): subagent implementations.
"""

from __future__ import annotations

import pytest


class TestAgentRegistry:
    """Tests for modules/agents/__init__.py AGENTS list."""

    def test_agents_list_is_not_empty(self) -> None:
        """AGENTS must contain at least one SubagentPlugin."""
        pytest.skip("Implemented in step 10 — feat(agents): tool-use subagent")

    def test_agent_names_are_unique(self) -> None:
        """No two agents in AGENTS may share the same name."""
        pytest.skip("Implemented in step 10 — feat(agents): tool-use subagent")

    def test_all_agents_implement_subagent_plugin(self) -> None:
        """Every item in AGENTS must be a SubagentPlugin instance."""
        pytest.skip("Implemented in step 10 — feat(agents): tool-use subagent")

    def test_agent_names_match_dispatch_table(self) -> None:
        """Every agent.name must appear in INTENT_DISPATCH."""
        pytest.skip("Implemented in step 13 — feat(core): graph nodes")
