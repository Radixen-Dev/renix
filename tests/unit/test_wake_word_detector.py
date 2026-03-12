"""Unit tests for openWakeWord detector wrapper."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

import pytest

from core.utils import WakeWordError
from modules.wake_word.detector import OpenWakeWordDetector


@dataclass
class _FakeModel:
    """Minimal fake model that returns predefined prediction scores."""

    scores: list[float] = field(default_factory=list)

    def predict(self, audio_frame: Any) -> dict[str, float]:
        del audio_frame
        score = self.scores.pop(0) if self.scores else 0.0
        return {"hey_renix": score}


class _FakeInputStream:
    """Minimal fake InputStream implementation used by tests."""

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.started = False
        self.stopped = False
        self.closed = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True

    def close(self) -> None:
        self.closed = True


class _RaisingInputStream(_FakeInputStream):
    """InputStream test double that fails during start."""

    def start(self) -> None:
        raise RuntimeError("stream start failure")


@dataclass
class _FakeSoundDeviceModule:
    """Minimal fake sounddevice module exposing InputStream."""

    stream_factory: type[_FakeInputStream]

    def __post_init__(self) -> None:
        self.InputStream = self.stream_factory


def _install_backends(
    monkeypatch: pytest.MonkeyPatch,
    model: _FakeModel,
    stream_factory: type[_FakeInputStream],
) -> None:
    """Install fake openWakeWord and sounddevice backends into sys.modules."""

    def _model_factory(**kwargs: Any) -> _FakeModel:
        del kwargs
        return model

    monkeypatch.setitem(
        sys.modules,
        "openwakeword",
        SimpleNamespace(Model=_model_factory),
    )
    monkeypatch.setitem(
        sys.modules,
        "sounddevice",
        _FakeSoundDeviceModule(stream_factory=stream_factory),
    )


def test_start_and_stop_lifecycle(monkeypatch: pytest.MonkeyPatch) -> None:
    """Detector start/stop should initialize and release stream resources."""
    _install_backends(
        monkeypatch,
        model=_FakeModel(scores=[]),
        stream_factory=_FakeInputStream,
    )

    detector = OpenWakeWordDetector(model_path="hey_renix")

    detector.start()

    assert detector._running is True
    assert isinstance(detector._stream, _FakeInputStream)
    assert detector._stream.started is True

    detector.stop()

    assert detector._running is False
    assert detector._stream is None


def test_wait_for_detection_blocks_until_threshold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """wait_for_detection should return after a score crosses threshold."""
    _install_backends(
        monkeypatch,
        model=_FakeModel(scores=[0.2, 0.9]),
        stream_factory=_FakeInputStream,
    )

    detector = OpenWakeWordDetector(model_path="hey_renix", threshold=0.5)
    detector.start()

    detector._audio_queue.put(SimpleNamespace(copy=lambda: "frame-1"))
    detector._audio_queue.put(SimpleNamespace(copy=lambda: "frame-2"))

    detector.wait_for_detection()

    detector.stop()


def test_start_wraps_stream_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    """start() should wrap backend startup failures as WakeWordError."""
    _install_backends(
        monkeypatch,
        model=_FakeModel(scores=[]),
        stream_factory=_RaisingInputStream,
    )

    detector = OpenWakeWordDetector(model_path="hey_renix")

    with pytest.raises(WakeWordError, match="Failed to start wake-word detector"):
        detector.start()
