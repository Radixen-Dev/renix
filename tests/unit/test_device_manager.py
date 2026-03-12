"""Unit tests for the audio device manager.

Verifies that:
- discover_devices() returns a DeviceConfig with valid fields.
- When input_device=None, falls back to system default (no AudioError).
- Invalid device names raise AudioError with a descriptive message.
- The returned DeviceConfig carries the requested sample_rate and chunk_size.

Implemented in step 5 — feat(audio): device autodiscovery.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from types import SimpleNamespace

import pytest

from core.utils import AudioError
from modules.audio.device_manager import DeviceConfig, discover_devices


@dataclass
class _FakeSoundDevice:
    """Minimal fake sounddevice API used by discover_devices tests."""

    devices: list[dict[str, object]]
    default_input: int = 0
    default_output: int = 1
    fail_on_samplerate: int | None = None

    def __post_init__(self) -> None:
        self.default = SimpleNamespace(device=(self.default_input, self.default_output))

    def query_devices(self) -> list[dict[str, object]]:
        return self.devices

    def check_input_settings(
        self,
        device: int,
        samplerate: int,
        channels: int,
    ) -> None:
        if (
            self.fail_on_samplerate is not None
            and samplerate == self.fail_on_samplerate
        ):
            raise RuntimeError("unsupported")

    def check_output_settings(
        self,
        device: int,
        samplerate: int,
        channels: int,
    ) -> None:
        if (
            self.fail_on_samplerate is not None
            and samplerate == self.fail_on_samplerate
        ):
            raise RuntimeError("unsupported")


class TestDiscoverDevices:
    """Tests for device_manager.discover_devices()."""

    @staticmethod
    def _install_fake_sd(
        monkeypatch: pytest.MonkeyPatch,
        fake_sd: _FakeSoundDevice,
    ) -> None:
        monkeypatch.setitem(sys.modules, "sounddevice", fake_sd)

    def test_none_inputs_return_default_config(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """discover_devices(None, None) must succeed and return a DeviceConfig."""
        fake_sd = _FakeSoundDevice(
            devices=[
                {"name": "Mic A", "max_input_channels": 1, "max_output_channels": 0},
                {
                    "name": "Speaker A",
                    "max_input_channels": 0,
                    "max_output_channels": 2,
                },
            ],
            default_input=0,
            default_output=1,
        )
        self._install_fake_sd(monkeypatch, fake_sd)

        cfg = discover_devices(None, None)

        assert isinstance(cfg, DeviceConfig)
        assert cfg.input_device == 0
        assert cfg.output_device == 1

    def test_invalid_device_name_raises_audio_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A device name that does not exist must raise AudioError."""
        fake_sd = _FakeSoundDevice(
            devices=[
                {"name": "Mic A", "max_input_channels": 1, "max_output_channels": 0},
                {
                    "name": "Speaker A",
                    "max_input_channels": 0,
                    "max_output_channels": 2,
                },
            ]
        )
        self._install_fake_sd(monkeypatch, fake_sd)

        with pytest.raises(AudioError, match="No input audio device matching"):
            discover_devices(input_device="definitely-missing")

    def test_sample_rate_is_preserved_in_config(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """The requested sample_rate must appear in the returned DeviceConfig."""
        fake_sd = _FakeSoundDevice(
            devices=[
                {"name": "Mic A", "max_input_channels": 1, "max_output_channels": 0},
                {
                    "name": "Speaker A",
                    "max_input_channels": 0,
                    "max_output_channels": 2,
                },
            ]
        )
        self._install_fake_sd(monkeypatch, fake_sd)

        cfg = discover_devices(sample_rate=22050, chunk_size=2048)

        assert cfg.sample_rate == 22050
        assert cfg.chunk_size == 2048

    def test_device_config_fields(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """DeviceConfig must expose device, sample_rate, and chunk_size fields."""
        fake_sd = _FakeSoundDevice(
            devices=[
                {"name": "Mic A", "max_input_channels": 1, "max_output_channels": 0},
                {
                    "name": "Speaker A",
                    "max_input_channels": 0,
                    "max_output_channels": 2,
                },
            ],
            default_input=-1,
            default_output=-1,
        )
        self._install_fake_sd(monkeypatch, fake_sd)

        cfg = discover_devices()

        assert hasattr(cfg, "input_device")
        assert hasattr(cfg, "output_device")
        assert hasattr(cfg, "sample_rate")
        assert hasattr(cfg, "chunk_size")
