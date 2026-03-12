"""Integration test — full reactive turn with mocked I/O.

Verifies end-to-end state transitions for a standard user-initiated turn:
    __start__ → listen → transcribe → orchestrator → respond → listen

All I/O modules (WakeWordDetector, AudioRecorder, Transcriber, Speaker, LLM)
are replaced with mocks. The test verifies:
- state["transcript"] is populated after transcribe.
- state["audio_bytes"] is None after transcribe.
- state["response"] is populated after orchestrator.
- The Speaker mock is called with the correct response text.

Implemented in step 14–15 — feat(core): parent graph / main.py + startup.
"""

from __future__ import annotations

import pytest


class TestGraphReactiveTurn:
    """Full reactive turn integration tests with mocked I/O."""

    def test_transcript_populated_after_transcribe(self) -> None:
        """state['transcript'] must be non-None after the transcribe node runs."""
        pytest.skip("Implemented in step 14 — feat(core): parent graph")

    def test_audio_bytes_cleared_after_transcribe(self) -> None:
        """state['audio_bytes'] must be None after transcribe (security requirement)."""
        pytest.skip("Implemented in step 14 — feat(core): parent graph")

    def test_response_populated_after_orchestrator(self) -> None:
        """state['response'] must be non-None when orchestrator produces a final answer."""
        pytest.skip("Implemented in step 14 — feat(core): parent graph")

    def test_speaker_called_with_response_text(self) -> None:
        """The Speaker mock's speak() must be called with state['response']."""
        pytest.skip("Implemented in step 14 — feat(core): parent graph")
