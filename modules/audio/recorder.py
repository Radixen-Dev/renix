"""Microphone capture — records one utterance and returns raw PCM bytes.

Implements the ``AudioRecorder`` interface from ``core/interfaces.py``.
Called exclusively by the ``listen`` node after wake-word detection.
"""

from __future__ import annotations

from core.interfaces import AudioRecorder
from core.utils import get_logger
from modules.audio.device_manager import DeviceConfig

logger = get_logger(__name__)


class SoundDeviceRecorder(AudioRecorder):
    """Microphone capture adapter backed by sounddevice.

    Records audio until silence is detected (VAD) or a maximum duration
    is reached. Returns raw 16 kHz mono PCM bytes.

    Attributes:
        device_config: Resolved device indices and audio parameters.
        max_duration_seconds: Maximum recording length before forced stop.
    """

    def __init__(
        self,
        device_config: DeviceConfig,
        max_duration_seconds: float = 10.0,
    ) -> None:
        """Initialise the recorder with resolved device configuration.

        Args:
            device_config: Resolved audio device parameters from device_manager.
            max_duration_seconds: Maximum recording duration in seconds.
        """
        # Implemented in step 6 will use wake-word; step 7 STT.
        # Full implementation in step 13 — feat(core): graph nodes
        self._device_config = device_config
        self._max_duration = max_duration_seconds

    def record(self) -> bytes:
        """Capture audio from the configured input device.

        Returns:
            Raw 16 kHz mono PCM audio as bytes.

        Raises:
            AudioError: If the microphone cannot be accessed or recording fails.
        """
        # Implemented in step 5 / step 13
        raise NotImplementedError("SoundDeviceRecorder.record implemented in step 5")
