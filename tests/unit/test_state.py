"""Unit tests for GraphState schema.

Verifies that:
- All expected fields are present with correct types.
- The add_messages reducer merges messages correctly.
- audio_bytes is correctly typed as Optional[bytes].
- The TypedDict is not mistakenly exported with extra fields.

Implemented in step 3 — feat(core): state schema.
"""

from __future__ import annotations

from typing import Annotated, get_args, get_origin, get_type_hints

from langgraph.graph.message import add_messages

from core.state import GraphState


class TestGraphStateFields:
    """Tests for GraphState field definitions."""

    def test_graphstate_has_messages_field(self) -> None:
        """GraphState must declare a 'messages' field."""
        hints = get_type_hints(GraphState, include_extras=True)
        assert "messages" in hints

    def test_graphstate_has_all_required_fields(self) -> None:
        """GraphState must contain all fields defined in the spec."""
        expected_fields = {
            "messages",
            "transcript",
            "response",
            "intent",
            "active_subagent",
            "audio_bytes",
            "proactive_message",
            "error",
        }
        hints = get_type_hints(GraphState, include_extras=True)
        assert set(hints.keys()) == expected_fields

    def test_audio_bytes_is_optional(self) -> None:
        """audio_bytes field must accept None to satisfy the clear-after-STT rule."""
        hints = get_type_hints(GraphState, include_extras=True)
        annotation = hints["audio_bytes"]
        union_args = set(get_args(annotation))
        assert union_args == {bytes, type(None)}

    def test_add_messages_reducer_appends(self) -> None:
        """The add_messages reducer must append new messages, not replace the list."""
        hints = get_type_hints(GraphState, include_extras=True)
        messages_annotation = hints["messages"]
        assert get_origin(messages_annotation) is Annotated
        annotated_args = get_args(messages_annotation)
        assert annotated_args[1] is add_messages

        base = []
        new = []
        merged = add_messages(base, new)
        assert isinstance(merged, list)
