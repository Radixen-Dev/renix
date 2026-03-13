"""Memory subagent — long-term memory recall and storage.

Intent labels dispatched here: ``"memory"``

Internal subgraph topology:
    classify → recall | store → END

Uses a SQLite backend at the path configured in ``config.yaml``
(``memory.db_path``). The check-pointer MemorySaver handles turn-to-turn
short-term memory; this agent handles cross-session long-term memory.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, cast

from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph

from core.interfaces import SubagentPlugin
from core.state import GraphState
from core.utils import AgentError, get_config, get_logger, load_config

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
        cfg = self._load_cfg()
        memory_cfg = cfg.get("memory")
        if not isinstance(memory_cfg, dict):
            raise AgentError("Missing 'memory' section in config.")

        db_path = memory_cfg.get("db_path", "data/memory.db")
        if not isinstance(db_path, str) or not db_path.strip():
            raise AgentError("memory.db_path must be a non-empty string.")

        enabled = bool(memory_cfg.get("long_term_enabled", True))
        store = _SQLiteMemoryStore(db_path)

        graph = StateGraph(GraphState)
        if not enabled:
            graph.add_node("memory_disabled", self._memory_disabled)
            graph.add_edge(START, "memory_disabled")
            graph.add_edge("memory_disabled", END)
            return cast(StateGraph, graph.compile())

        graph.add_node("classify", self._classify)
        graph.add_node("recall", lambda state: self._recall(state, store))
        graph.add_node("store", lambda state: self._store(state, store))

        graph.add_edge(START, "classify")
        graph.add_conditional_edges(
            "classify",
            self._route_after_classify,
            {
                "recall": "recall",
                "store": "store",
            },
        )
        graph.add_edge("recall", END)
        graph.add_edge("store", END)
        return cast(StateGraph, graph.compile())

    def _classify(self, state: GraphState) -> dict[str, Any]:
        """No-op classifier node used to branch into store vs recall."""
        _ = state
        return {}

    def _route_after_classify(self, state: GraphState) -> str:
        """Route to store when user asks to remember; otherwise recall."""
        text = self._latest_user_text(state)
        if _looks_like_store_request(text):
            return "store"
        return "recall"

    def _store(
        self,
        state: GraphState,
        store: _SQLiteMemoryStore,
    ) -> dict[str, Any]:
        """Persist the latest user message as long-term memory."""
        text = self._latest_user_text(state)
        if not text:
            return {
                "messages": [
                    AIMessage(content="I could not find anything to store in memory.")
                ]
            }

        store.add_memory(text)
        return {
            "messages": [
                AIMessage(content="Stored. I will remember that for future sessions.")
            ]
        }

    def _recall(
        self,
        state: GraphState,
        store: _SQLiteMemoryStore,
    ) -> dict[str, Any]:
        """Retrieve matching memories for the latest user query."""
        query = _normalize_recall_query(self._latest_user_text(state))
        memories = store.search(query=query, limit=5)
        if not memories:
            return {
                "messages": [
                    AIMessage(content="I don't have a matching long-term memory yet.")
                ]
            }

        joined = "\n".join(f"- {item}" for item in memories)
        return {"messages": [AIMessage(content=f"Relevant memories:\n{joined}")]}

    def _memory_disabled(self, state: GraphState) -> dict[str, Any]:
        """Return a message when long-term memory is disabled in config."""
        _ = state
        return {
            "messages": [
                AIMessage(
                    content=(
                        "Long-term memory is disabled in configuration "
                        "(memory.long_term_enabled=false)."
                    )
                )
            ]
        }

    def _latest_user_text(self, state: GraphState) -> str:
        """Extract the most recent human/user message text from state."""
        messages = state.get("messages", [])
        if not isinstance(messages, list):
            return ""

        for message in reversed(messages):
            msg_type = str(getattr(message, "type", ""))
            if msg_type == "human":
                content = getattr(message, "content", "")
                return str(content).strip()
        return ""

    def _load_cfg(self) -> dict[str, Any]:
        """Return loaded config, loading from disk if needed."""
        try:
            return get_config()
        except Exception:
            return load_config()


class _SQLiteMemoryStore:
    """Simple SQLite-backed long-term memory store."""

    def __init__(self, db_path: str) -> None:
        """Initialize database path and ensure schema exists."""
        self._db_path = Path(db_path)
        if not self._db_path.is_absolute():
            self._db_path = Path.cwd() / self._db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create memory table if it does not already exist."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def add_memory(self, content: str) -> None:
        """Persist one memory record."""
        with sqlite3.connect(self._db_path) as conn:
            conn.execute("INSERT INTO memories (content) VALUES (?)", (content,))
            conn.commit()

    def search(self, query: str, limit: int = 5) -> list[str]:
        """Return recent memories matching query text, or most recent entries."""
        safe_limit = max(1, min(limit, 20))
        with sqlite3.connect(self._db_path) as conn:
            if query.strip():
                rows = conn.execute(
                    """
                    SELECT content
                    FROM memories
                    WHERE content LIKE ?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (f"%{query}%", safe_limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT content
                    FROM memories
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (safe_limit,),
                ).fetchall()
        return [str(row[0]) for row in rows]


def _looks_like_store_request(text: str) -> bool:
    """Return whether text likely asks to save something to long-term memory."""
    lowered = text.lower()

    recall_markers = (
        "what do you remember",
        "do you remember",
        "can you remember",
        "recall",
    )
    if any(marker in lowered for marker in recall_markers):
        return False

    markers = (
        "remember that",
        "remember this",
        "remember",
        "memorize",
        "store this",
        "save this",
        "note this",
    )
    return any(marker in lowered for marker in markers)


def _normalize_recall_query(text: str) -> str:
    """Strip recall prompt wrappers to improve memory lookup matching."""
    lowered = text.lower().strip()
    markers = (
        "what do you remember about",
        "do you remember",
        "can you remember",
        "recall",
    )
    for marker in markers:
        if lowered.startswith(marker):
            cleaned = lowered.removeprefix(marker).strip(" ?!.,")
            return cleaned or lowered
    return lowered
