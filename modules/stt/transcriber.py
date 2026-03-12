"""faster-whisper STT transcriber wrapper.

Implements the ``Transcriber`` interface from ``core/interfaces.py``.
Wraps the faster-whisper library to convert raw PCM audio bytes to text.

Security note: Transcribed content must never be logged at INFO level or above.
"""

from __future__ import annotations

from array import array
from typing import Any

from core.interfaces import Transcriber
from core.utils import TranscriptionError, get_logger

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
        if not model_size.strip():
            raise TranscriptionError("stt.model_size must be a non-empty string.")
        if device not in {"cpu", "cuda"}:
            raise TranscriptionError(
                "stt.device must be 'cpu' or 'cuda', "
                f"got '{device}'."
            )

        self._model_size = model_size
        self._device = device
        self._language: str | None = language if language else None
        self._model: Any = self._load_model()

    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe raw PCM audio bytes to text using faster-whisper.

        Args:
            audio_data: Raw 16 kHz mono PCM audio as bytes.

        Returns:
            Transcribed text string. Empty string if no speech detected.

        Raises:
            TranscriptionError: If the model fails to process the audio.
        """
        if not audio_data:
            return ""

        samples = self._pcm16_bytes_to_float32(audio_data)
        if not samples:
            return ""

        try:
            segments, _info = self._model.transcribe(
                samples,
                language=self._language,
            )
        except Exception as exc:
            raise TranscriptionError(f"STT transcription failed: {exc}") from exc

        text_parts: list[str] = []
        for segment in segments:
            text = str(getattr(segment, "text", "")).strip()
            if text:
                text_parts.append(text)

        transcript = " ".join(text_parts).strip()
        # Never log transcripts at INFO level or above.
        logger.debug("STT produced transcript chars=%d", len(transcript))
        return transcript

    def _load_model(self) -> Any:
        """Load and return faster-whisper WhisperModel instance."""
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise TranscriptionError(
                "faster-whisper is not installed. "
                "Install requirements.txt dependencies."
            ) from exc

        try:
            return WhisperModel(self._model_size, device=self._device)
        except Exception as exc:
            raise TranscriptionError(f"Failed to load Whisper model: {exc}") from exc

    def _pcm16_bytes_to_float32(self, audio_data: bytes) -> list[float]:
        """Convert 16-bit PCM bytes to normalized float waveform values."""
        if len(audio_data) % 2 != 0:
            raise TranscriptionError(
                "audio_data length must be even for 16-bit PCM input."
            )

        pcm = array("h")
        pcm.frombytes(audio_data)
        if not pcm:
            return []
        return [float(sample) / 32768.0 for sample in pcm]
