"""Integration test — proactive initiation path.

Verifies end-to-end state transitions for a scheduler-initiated turn:
    __start__ → scheduler → orchestrator → respond → listen

All I/O modules (Speaker, LLM) are replaced with mocks. The test verifies:
- state["proactive_message"] is set by the scheduler node.
- state["transcript"] remains None throughout the proactive path.
- The orchestrator generates a response from proactive_message.
- The Speaker mock is called once with the generated response.

Implemented in step 14–15 — feat(core): parent graph / main.py + startup.
"""

from __future__ import annotations

import pytest


class TestGraphProactiveTurn:
    """Full proactive turn integration tests with mocked I/O."""

    def test_scheduler_sets_proactive_message(self) -> None:
        """state['proactive_message'] must be non-None after the scheduler node."""
        pytest.skip("Implemented in step 14 — feat(core): parent graph")

    def test_transcript_is_none_in_proactive_turn(self) -> None:
        """state['transcript'] must remain None throughout a proactive turn."""
        pytest.skip("Implemented in step 14 — feat(core): parent graph")

    def test_response_generated_from_proactive_message(self) -> None:
        """The orchestrator must produce a response when proactive_message is set."""
        pytest.skip("Implemented in step 14 — feat(core): parent graph")

    def test_speaker_called_once_in_proactive_turn(self) -> None:
        """Speaker.speak() must be called exactly once per proactive turn."""
        pytest.skip("Implemented in step 14 — feat(core): parent graph")
