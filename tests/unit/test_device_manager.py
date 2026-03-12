"""Unit tests for the audio device manager.

Verifies that:
- discover_devices() returns a DeviceConfig with valid fields.
- When input_device=None, falls back to system default (no AudioError).
- Invalid device names raise AudioError with a descriptive message.
- The returned DeviceConfig carries the requested sample_rate and chunk_size.

Implemented in step 5 — feat(audio): device autodiscovery.
"""

from __future__ import annotations

import pytest


class TestDiscoverDevices:
    """Tests for device_manager.discover_devices()."""

    def test_none_inputs_return_default_config(self) -> None:
        """discover_devices(None, None) must succeed and return a DeviceConfig."""
        pytest.skip("Implemented in step 5 — feat(audio): device autodiscovery")

    def test_invalid_device_name_raises_audio_error(self) -> None:
        """A device name that does not exist must raise AudioError."""
        pytest.skip("Implemented in step 5 — feat(audio): device autodiscovery")

    def test_sample_rate_is_preserved_in_config(self) -> None:
        """The requested sample_rate must appear in the returned DeviceConfig."""
        pytest.skip("Implemented in step 5 — feat(audio): device autodiscovery")

    def test_device_config_fields(self) -> None:
        """DeviceConfig must expose device, sample_rate, and chunk_size fields."""
        pytest.skip("Implemented in step 5 — feat(audio): device autodiscovery")
