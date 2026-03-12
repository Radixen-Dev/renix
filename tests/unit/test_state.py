"""Unit tests for GraphState schema.

Verifies that:
- All expected fields are present with correct types.
- The add_messages reducer merges messages correctly.
- audio_bytes is correctly typed as Optional[bytes].
- The TypedDict is not mistakenly exported with extra fields.

Implemented in step 3 — feat(core): state schema.
"""

from __future__ import annotations

import pytest


class TestGraphStateFields:
    """Tests for GraphState field definitions."""

    def test_graphstate_has_messages_field(self) -> None:
        """GraphState must declare a 'messages' field."""
        # Implemented in step 3
        pytest.skip("Implemented in step 3 — feat(core): state schema")

    def test_graphstate_has_all_required_fields(self) -> None:
        """GraphState must contain all fields defined in the spec."""
        # Implemented in step 3
        pytest.skip("Implemented in step 3 — feat(core): state schema")

    def test_audio_bytes_is_optional(self) -> None:
        """audio_bytes field must accept None to satisfy the clear-after-STT rule."""
        # Implemented in step 3
        pytest.skip("Implemented in step 3 — feat(core): state schema")

    def test_add_messages_reducer_appends(self) -> None:
        """The add_messages reducer must append new messages, not replace the list."""
        # Implemented in step 3
        pytest.skip("Implemented in step 3 — feat(core): state schema")
