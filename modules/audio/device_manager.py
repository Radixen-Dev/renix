"""Audio device autodiscovery and validation.

This is the ONLY file in the project that contains platform-specific logic.
All differences between Raspberry Pi OS (ARM) and Windows 10/11 are handled
here. The rest of the codebase is platform-agnostic.

Responsibilities:
- Enumerate available input and output audio devices.
- Resolve device names/indices from config.yaml (or fall back to system defaults).
- Validate that the resolved devices are capable of the required sample rate.
- Expose a single DeviceConfig dataclass consumed by recorder.py and speaker.py.
"""

from __future__ import annotations

# Implemented in step 5 — feat(audio): device autodiscovery
# Platform-specific logic for Windows and Raspberry Pi OS goes here.

from dataclasses import dataclass
from typing import Optional

from core.utils import AudioError, get_logger

logger = get_logger(__name__)


@dataclass
class DeviceConfig:
    """Resolved audio device configuration.

    Attributes:
        input_device: sounddevice device index for the microphone, or ``None``
            to use the system default.
        output_device: sounddevice device index for the speaker, or ``None``
            to use the system default.
        sample_rate: Target sample rate in Hz (default 16000).
        chunk_size: Frames per buffer chunk (default 1024).
    """

    input_device: Optional[int]
    output_device: Optional[int]
    sample_rate: int = 16000
    chunk_size: int = 1024


def discover_devices(
    input_device: Optional[str | int] = None,
    output_device: Optional[str | int] = None,
    sample_rate: int = 16000,
    chunk_size: int = 1024,
) -> DeviceConfig:
    """Autodiscover and validate audio input/output devices.

    Resolves device names or indices from config values. Falls back to the
    system default if ``None`` is provided. Validates that the resolved
    devices support the requested sample rate.

    Args:
        input_device: Device name substring, integer index, or ``None`` for
            the system default.
        output_device: Device name substring, integer index, or ``None`` for
            the system default.
        sample_rate: Required sample rate in Hz.
        chunk_size: Frames per recording chunk.

    Returns:
        A ``DeviceConfig`` with resolved integer device indices.

    Raises:
        AudioError: If a specified device cannot be found or does not support
            the requested sample rate.
    """
    # Implemented in step 5 — feat(audio): device autodiscovery
    raise NotImplementedError("discover_devices implemented in step 5")
