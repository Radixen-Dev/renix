"""pyttsx3 TTS speaker wrapper.

Implements the ``Speaker`` interface from ``core/interfaces.py``. Wraps the
pyttsx3 library to convert text to speech and play it through the configured
output device.
"""

from __future__ import annotations

from typing import Optional

from core.interfaces import Speaker
from core.utils import TTSError, get_logger

logger = get_logger(__name__)


class Pyttsx3Speaker(Speaker):
    """TTS adapter backed by pyttsx3.

    Initialises the pyttsx3 engine on construction and applies the configured
    voice, rate, and volume settings.

    Attributes:
        rate: Words-per-minute speech rate.
        volume: Output volume (0.0–1.0).
        voice_id: System voice identifier string, or ``None`` for the default.
    """

    def __init__(
        self,
        rate: int = 175,
        volume: float = 1.0,
        voice_id: Optional[str] = None,
    ) -> None:
        """Initialise the pyttsx3 engine with the specified settings.

        Args:
            rate: Speech rate in words per minute.
            volume: Playback volume between 0.0 and 1.0.
            voice_id: Platform voice identifier, or ``None`` for the system
                default voice.

        Raises:
            TTSError: If the pyttsx3 engine cannot be initialised.
        """
        self._rate = rate
        self._volume = volume
        self._voice_id = voice_id

    def speak(self, text: str) -> None:
        """Convert text to speech and play it through the output device.

        Args:
            text: The response string to speak aloud.

        Raises:
            TTSError: If audio output fails.
        """
        # Implemented in step 8 — feat(tts): speaker
        raise NotImplementedError("Pyttsx3Speaker.speak implemented in step 8")
