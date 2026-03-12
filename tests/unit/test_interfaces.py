"""Unit tests for core interface contracts.

Verifies that each interface in ``core/interfaces.py`` remains abstract and
exposes the required method signatures expected by modules and graph nodes.

Implemented in step 4 — feat(core): interfaces.
"""

from __future__ import annotations

import inspect

from core.interfaces import (
    AudioRecorder,
    Speaker,
    SubagentPlugin,
    ToolPlugin,
    Transcriber,
    WakeWordDetector,
)


class TestPluginInterfaces:
    """Tests for plugin ABC contracts."""

    def test_subagent_plugin_is_abstract(self) -> None:
        """SubagentPlugin must remain abstract and require build()."""
        assert inspect.isabstract(SubagentPlugin)
        assert "build" in SubagentPlugin.__abstractmethods__

    def test_tool_plugin_is_abstract(self) -> None:
        """ToolPlugin must remain abstract and require run()."""
        assert inspect.isabstract(ToolPlugin)
        assert "run" in ToolPlugin.__abstractmethods__


class TestAudioInterfaces:
    """Tests for audio and I/O ABC contracts."""

    def test_wake_word_detector_abstract_methods(self) -> None:
        """WakeWordDetector must define start/stop/wait_for_detection."""
        assert inspect.isabstract(WakeWordDetector)
        required = {"start", "stop", "wait_for_detection"}
        assert required.issubset(WakeWordDetector.__abstractmethods__)

    def test_audio_recorder_abstract_method(self) -> None:
        """AudioRecorder must define record()."""
        assert inspect.isabstract(AudioRecorder)
        assert "record" in AudioRecorder.__abstractmethods__

    def test_transcriber_abstract_method(self) -> None:
        """Transcriber must define transcribe()."""
        assert inspect.isabstract(Transcriber)
        assert "transcribe" in Transcriber.__abstractmethods__

    def test_speaker_abstract_method(self) -> None:
        """Speaker must define speak()."""
        assert inspect.isabstract(Speaker)
        assert "speak" in Speaker.__abstractmethods__
