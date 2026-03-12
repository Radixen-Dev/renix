"""pyttsx3 TTS speaker wrapper.

Implements the ``Speaker`` interface from ``core/interfaces.py``. Wraps the
pyttsx3 library to convert text to speech and play it through the configured
output device.
"""

from __future__ import annotations

from typing import Any

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
        voice_id: str | None = None,
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
        if rate <= 0:
            raise TTSError(f"tts.rate must be > 0, got {rate}.")
        if volume < 0.0 or volume > 1.0:
            raise TTSError(f"tts.volume must be in [0.0, 1.0], got {volume}.")

        self._rate = rate
        self._volume = volume
        self._voice_id = voice_id
        self._engine = self._init_engine()

    def speak(self, text: str) -> None:
        """Convert text to speech and play it through the output device.

        Args:
            text: The response string to speak aloud.

        Raises:
            TTSError: If audio output fails.
        """
        if not text.strip():
            return

        try:
            self._engine.say(text)
            self._engine.runAndWait()
        except Exception as exc:
            raise TTSError(f"TTS playback failed: {exc}") from exc

    def _init_engine(self) -> Any:
        """Initialize and configure the pyttsx3 engine instance."""
        try:
            import pyttsx3
        except ImportError as exc:
            raise TTSError(
                "pyttsx3 is not installed. Install requirements.txt dependencies."
            ) from exc

        try:
            engine = pyttsx3.init()
            engine.setProperty("rate", self._rate)
            engine.setProperty("volume", self._volume)
            if self._voice_id:
                engine.setProperty("voice", self._voice_id)
            return engine
        except Exception as exc:
            raise TTSError(f"Failed to initialize TTS engine: {exc}") from exc
