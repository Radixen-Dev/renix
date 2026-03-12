"""faster-whisper STT transcriber wrapper.

Implements the ``Transcriber`` interface from ``core/interfaces.py``.
Wraps the faster-whisper library to convert raw PCM audio bytes to text.

Security note: Transcribed content must never be logged at INFO level or above.
"""

from __future__ import annotations

from core.interfaces import Transcriber
from core.utils import get_logger

logger = get_logger(__name__)


class WhisperTranscriber(Transcriber):
    """STT adapter backed by faster-whisper.

    Loads the Whisper model on construction. Accepts raw 16 kHz mono PCM
    bytes and returns a transcribed text string.

    Attributes:
        model_size: Whisper model variant (tiny, base, small, medium, large).
        device: Inference device (``"cpu"`` or ``"cuda"``).
        language: BCP-47 language code (e.g. ``"en"``). Pass ``None`` for
            automatic language detection.
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        language: str = "en",
    ) -> None:
        """Load the faster-whisper model.

        Args:
            model_size: Whisper model size variant.
            device: Target compute device for inference.
            language: Expected spoken language code, or ``None`` for auto.

        Raises:
            TranscriptionError: If the model cannot be loaded.
        """
        self._model_size = model_size
        self._device = device
        self._language: str | None = language if language else None

    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe raw PCM audio bytes to text using faster-whisper.

        Args:
            audio_data: Raw 16 kHz mono PCM audio as bytes.

        Returns:
            Transcribed text string. Empty string if no speech detected.

        Raises:
            TranscriptionError: If the model fails to process the audio.
        """
        # Implemented in step 7 — feat(stt): transcriber
        raise NotImplementedError("WhisperTranscriber.transcribe implemented in step 7")
