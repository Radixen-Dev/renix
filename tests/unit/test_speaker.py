"""Unit tests for the pyttsx3 speaker wrapper."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from core.utils import TTSError
from modules.tts.speaker import Pyttsx3Speaker


@dataclass
class _FakeEngine:
    """Minimal fake pyttsx3 engine for speaker tests."""

    should_fail_run: bool = False

    def __post_init__(self) -> None:
        self.properties: dict[str, object] = {}
        self.spoken: list[str] = []

    def setProperty(self, key: str, value: object) -> None:  # noqa: N802
        self.properties[key] = value

    def say(self, text: str) -> None:
        self.spoken.append(text)

    def runAndWait(self) -> None:  # noqa: N802
        if self.should_fail_run:
            raise RuntimeError("playback failed")


def _install_pyttsx3(
    monkeypatch: pytest.MonkeyPatch,
    *,
    should_fail_init: bool = False,
    should_fail_run: bool = False,
) -> _FakeEngine:
    """Install a fake pyttsx3 module in sys.modules."""
    engine = _FakeEngine(should_fail_run=should_fail_run)

    def _init() -> _FakeEngine:
        if should_fail_init:
            raise RuntimeError("init failed")
        return engine

    monkeypatch.setitem(sys.modules, "pyttsx3", SimpleNamespace(init=_init))
    return engine


def test_speaker_initializes_engine_and_properties(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Constructor should initialize engine and apply rate/volume/voice settings."""
    engine = _install_pyttsx3(monkeypatch)

    Pyttsx3Speaker(rate=180, volume=0.7, voice_id="voice-1")

    assert engine.properties["rate"] == 180
    assert engine.properties["volume"] == 0.7
    assert engine.properties["voice"] == "voice-1"


def test_speak_sends_text_to_engine(monkeypatch: pytest.MonkeyPatch) -> None:
    """speak() should queue text and run playback."""
    engine = _install_pyttsx3(monkeypatch)
    speaker = Pyttsx3Speaker()

    speaker.speak("hello from renix")

    assert engine.spoken == ["hello from renix"]


def test_speak_empty_text_is_noop(monkeypatch: pytest.MonkeyPatch) -> None:
    """speak() should ignore empty or whitespace-only text."""
    engine = _install_pyttsx3(monkeypatch)
    speaker = Pyttsx3Speaker()

    speaker.speak("   ")

    assert engine.spoken == []


def test_invalid_constructor_values_raise(monkeypatch: pytest.MonkeyPatch) -> None:
    """Invalid rate/volume constructor values should raise TTSError."""
    _install_pyttsx3(monkeypatch)

    with pytest.raises(TTSError, match="tts.rate must be > 0"):
        Pyttsx3Speaker(rate=0)

    with pytest.raises(TTSError, match=r"tts.volume must be in \[0.0, 1.0\]"):
        Pyttsx3Speaker(volume=1.5)


def test_init_failure_wrapped_as_tts_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """Engine init failures should be wrapped as TTSError."""
    _install_pyttsx3(monkeypatch, should_fail_init=True)

    with pytest.raises(TTSError, match="Failed to initialize TTS engine"):
        Pyttsx3Speaker()


def test_playback_failure_wrapped_as_tts_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Playback failures should be wrapped as TTSError."""
    _install_pyttsx3(monkeypatch, should_fail_run=True)
    speaker = Pyttsx3Speaker()

    with pytest.raises(TTSError, match="TTS playback failed"):
        speaker.speak("test")
