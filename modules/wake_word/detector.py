"""openWakeWord detector wrapper.

Implements the ``WakeWordDetector`` interface from ``core/interfaces.py``.
Wraps the openWakeWord library to block until the configured wake-word model
fires above the configured confidence threshold.
"""

from __future__ import annotations

from core.interfaces import WakeWordDetector
from core.utils import WakeWordError, get_logger

logger = get_logger(__name__)


class OpenWakeWordDetector(WakeWordDetector):
    """Wake-word detector backed by openWakeWord.

    Loads the specified model on construction and starts a background audio
    stream on ``start()``. ``wait_for_detection()`` blocks until the model
    fires above ``threshold``.

    Attributes:
        model_path: Path or name of the openWakeWord model to load.
        threshold: Confidence score (0.0–1.0) required to trigger detection.
        cooldown_seconds: Minimum seconds between consecutive detections.
    """

    def __init__(
        self,
        model_path: str,
        threshold: float = 0.5,
        cooldown_seconds: float = 2.0,
    ) -> None:
        """Initialise the detector without starting the audio stream.

        Args:
            model_path: openWakeWord model path or built-in model name.
            threshold: Detection confidence threshold (0.0–1.0).
            cooldown_seconds: Minimum gap between detections to prevent
                repeated triggers.
        """
        self._model_path = model_path
        self._threshold = threshold
        self._cooldown = cooldown_seconds

    def start(self) -> None:
        """Load the model and start the background audio stream.

        Raises:
            WakeWordError: If the model cannot be loaded or the audio stream
                cannot be opened.
        """
        # Implemented in step 6 — feat(wake-word): detector
        raise NotImplementedError("OpenWakeWordDetector.start implemented in step 6")

    def stop(self) -> None:
        """Stop the background audio stream and release resources."""
        # Implemented in step 6 — feat(wake-word): detector
        raise NotImplementedError("OpenWakeWordDetector.stop implemented in step 6")

    def wait_for_detection(self) -> None:
        """Block until the wake word is detected above the threshold.

        Raises:
            WakeWordError: If the detector encounters an unrecoverable error
                while waiting.
        """
        # Implemented in step 6 — feat(wake-word): detector
        raise NotImplementedError("OpenWakeWordDetector.wait_for_detection implemented in step 6")
