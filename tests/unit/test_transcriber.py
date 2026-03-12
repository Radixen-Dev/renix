"""Unit tests for the faster-whisper transcriber wrapper."""

from __future__ import annotations

import struct
import sys
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

import pytest

from core.utils import TranscriptionError
from modules.stt.transcriber import WhisperTranscriber


@dataclass
class _FakeSegment:
    """Minimal transcription segment with a text field."""

    text: str


class _FakeWhisperModel:
    """Minimal fake faster-whisper model for tests."""

    def __init__(
        self,
        model_size: str,
        device: str,
        should_raise: bool = False,
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.should_raise = should_raise

    def transcribe(
        self,
        audio: Any,
        language: str | None,
    ) -> tuple[list[_FakeSegment], dict[str, object]]:
        del audio, language
        if self.should_raise:
            raise RuntimeError("inference failed")
        return [_FakeSegment("hello"), _FakeSegment("world")], {}


def _install_faster_whisper_module(
    monkeypatch: pytest.MonkeyPatch,
    should_raise_on_load: bool = False,
    should_raise_on_transcribe: bool = False,
) -> None:
    """Install a fake faster_whisper module in sys.modules."""

    def _factory(model_size: str, device: str) -> _FakeWhisperModel:
        if should_raise_on_load:
            raise RuntimeError("load failed")
        return _FakeWhisperModel(
            model_size=model_size,
            device=device,
            should_raise=should_raise_on_transcribe,
        )

    monkeypatch.setitem(
        sys.modules,
        "faster_whisper",
        SimpleNamespace(WhisperModel=_factory),
    )


def test_transcriber_loads_model(monkeypatch: pytest.MonkeyPatch) -> None:
    """Constructor should load WhisperModel with configured model and device."""
    _install_faster_whisper_module(monkeypatch)

    transcriber = WhisperTranscriber(model_size="small", device="cpu", language="en")

    model = transcriber._model
    assert isinstance(model, _FakeWhisperModel)
    assert model.model_size == "small"
    assert model.device == "cpu"


def test_transcribe_returns_joined_text(monkeypatch: pytest.MonkeyPatch) -> None:
    """transcribe() should join recognized segment text with spaces."""
    _install_faster_whisper_module(monkeypatch)

    transcriber = WhisperTranscriber(language="en")
    audio_data = struct.pack("<hhh", 1000, -1000, 2000)

    result = transcriber.transcribe(audio_data)

    assert result == "hello world"


def test_transcribe_empty_bytes_returns_empty(monkeypatch: pytest.MonkeyPatch) -> None:
    """transcribe() should return empty string for empty audio bytes."""
    _install_faster_whisper_module(monkeypatch)

    transcriber = WhisperTranscriber(language="en")

    assert transcriber.transcribe(b"") == ""


def test_model_load_failure_raises_transcription_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Model construction failures should be wrapped as TranscriptionError."""
    _install_faster_whisper_module(monkeypatch, should_raise_on_load=True)

    with pytest.raises(TranscriptionError, match="Failed to load Whisper model"):
        WhisperTranscriber()


def test_inference_failure_raises_transcription_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Inference failures should be wrapped as TranscriptionError."""
    _install_faster_whisper_module(monkeypatch, should_raise_on_transcribe=True)

    transcriber = WhisperTranscriber(language="en")
    audio_data = struct.pack("<hhh", 1000, -1000, 2000)

    with pytest.raises(TranscriptionError, match="STT transcription failed"):
        transcriber.transcribe(audio_data)


def test_odd_length_pcm_raises_transcription_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Odd-length PCM bytes should raise a TranscriptionError."""
    _install_faster_whisper_module(monkeypatch)

    transcriber = WhisperTranscriber(language="en")

    with pytest.raises(TranscriptionError, match="length must be even"):
        transcriber.transcribe(b"\x01")
