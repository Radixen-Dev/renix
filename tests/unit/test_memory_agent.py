"""Unit tests for the memory subagent SQLite backend and graph behavior."""

from __future__ import annotations

from pathlib import Path

from langchain_core.messages import HumanMessage

from modules.agents.memory_agent import MemoryAgent, _SQLiteMemoryStore


def _base_state(messages: list[object]) -> dict[str, object]:
    """Build minimal GraphState payload used for subagent invocation tests."""
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


class TestSQLiteMemoryStore:
    """Tests for low-level SQLite store behavior."""

    def test_add_and_search_roundtrip(self, tmp_path: Path) -> None:
        """Stored memory rows should be searchable by query substring."""
        db_file = tmp_path / "memory.db"
        store = _SQLiteMemoryStore(str(db_file))

        store.add_memory("my favorite color is blue")
        results = store.search("favorite color")

        assert results
        assert "favorite color" in results[0]


class TestMemoryAgent:
    """Tests for MemoryAgent graph behavior."""

    def test_store_then_recall(self, tmp_path: Path) -> None:
        """Agent should persist remembered text and later recall it."""
        db_file = tmp_path / "memory.db"
        agent = MemoryAgent()
        agent._load_cfg = lambda: {  # type: ignore[assignment]
            "memory": {
                "long_term_enabled": True,
                "db_path": str(db_file),
            }
        }
        compiled = agent.build()

        store_state = _base_state(
            [HumanMessage(content="Remember that my favorite color is blue")]
        )
        store_result = compiled.invoke(store_state)

        assert "Stored" in str(store_result["messages"][-1].content)

        recall_state = _base_state(
            [HumanMessage(content="what do you remember about my favorite color")]
        )
        recall_result = compiled.invoke(recall_state)

        assert "Relevant memories" in str(recall_result["messages"][-1].content)
        assert "favorite color is blue" in str(recall_result["messages"][-1].content)

    def test_disabled_memory_returns_notice(self, tmp_path: Path) -> None:
        """When long-term memory is disabled, agent should return a notice."""
        db_file = tmp_path / "memory.db"
        agent = MemoryAgent()
        agent._load_cfg = lambda: {  # type: ignore[assignment]
            "memory": {
                "long_term_enabled": False,
                "db_path": str(db_file),
            }
        }
        compiled = agent.build()

        result = compiled.invoke(_base_state([HumanMessage(content="remember this")]))

        assert "Long-term memory is disabled" in str(result["messages"][-1].content)
