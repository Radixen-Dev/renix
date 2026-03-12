"""Memory subagent — long-term memory recall and storage.

Intent labels dispatched here: ``"memory"``

Internal subgraph topology:
    classify → recall | store → END

Uses a SQLite backend at the path configured in ``config.yaml``
(``memory.db_path``). The check-pointer MemorySaver handles turn-to-turn
short-term memory; this agent handles cross-session long-term memory.
"""

from __future__ import annotations

from langgraph.graph import StateGraph

from core.interfaces import SubagentPlugin
from core.utils import get_logger

logger = get_logger(__name__)


class MemoryAgent(SubagentPlugin):
    """Subagent for cross-session long-term memory recall and storage.

    Stores and retrieves facts, preferences, and context across separate
    conversation sessions using a local SQLite database.

    Attributes:
        name: ``"memory"`` — must match the intent label in route.py.
        description: Shown to the orchestrator to explain when to delegate.
    """

    name = "memory"
    description = (
        "Stores or retrieves long-term memories about the user — preferences, "
        "past conversations, important facts. Delegate here when the request "
        "involves remembering or recalling information across sessions."
    )

    def build(self) -> StateGraph:
        """Build the memory subgraph with recall and store branches.

        Returns:
            Compiled LangGraph StateGraph for memory operations.

        Raises:
            AgentError: If the SQLite database cannot be opened or created.
        """
        # Implemented in step 11 — feat(agents): memory subagent
        raise NotImplementedError("MemoryAgent.build implemented in step 11")
