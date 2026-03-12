"""openWakeWord detector wrapper.

Implements the ``WakeWordDetector`` interface from ``core/interfaces.py``.
Wraps the openWakeWord library to block until the configured wake-word model
fires above the configured confidence threshold.
"""

from __future__ import annotations

import queue
import time
from collections.abc import Callable
from typing import Any

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

        Raises:
            WakeWordError: If constructor arguments are invalid.
        """
        if not model_path.strip():
            raise WakeWordError("wake_word.model_path must be a non-empty string.")
        if threshold < 0.0 or threshold > 1.0:
            raise WakeWordError(
                f"wake_word.threshold must be in [0.0, 1.0], got {threshold}."
            )
        if cooldown_seconds < 0.0:
            raise WakeWordError(
                "wake_word.cooldown_seconds must be >= 0.0, "
                f"got {cooldown_seconds}."
            )

        self._model_path = model_path
        self._threshold = threshold
        self._cooldown = cooldown_seconds
        self._model: Any | None = None
        self._stream: Any | None = None
        self._audio_queue: queue.Queue[Any] = queue.Queue(maxsize=16)
        self._running = False
        self._last_detection_ts = 0.0

    def start(self) -> None:
        """Load the model and start the background audio stream.

        Raises:
            WakeWordError: If the model cannot be loaded or the audio stream
                cannot be opened.
        """
        if self._running:
            return

        try:
            openwakeword = _load_openwakeword_module()
            sd = _load_sounddevice_module()
            self._model = _build_openwakeword_model(openwakeword, self._model_path)
            self._stream = sd.InputStream(
                samplerate=16000,
                channels=1,
                blocksize=1280,
                dtype="int16",
                callback=self._audio_callback,
            )
            self._stream.start()
            self._running = True
            self._last_detection_ts = 0.0
            logger.info(
                "Wake-word detector started model=%s threshold=%.2f cooldown=%.2fs",
                self._model_path,
                self._threshold,
                self._cooldown,
            )
        except WakeWordError:
            self.stop()
            raise
        except Exception as exc:
            self.stop()
            raise WakeWordError(f"Failed to start wake-word detector: {exc}") from exc

    def stop(self) -> None:
        """Stop the background audio stream and release resources."""
        self._running = False

        if self._stream is not None:
            try:
                self._stream.stop()
            except Exception:
                logger.warning("Ignoring wake-word stream stop failure", exc_info=True)
            try:
                self._stream.close()
            except Exception:
                logger.warning("Ignoring wake-word stream close failure", exc_info=True)

        self._stream = None
        self._model = None
        self._audio_queue = queue.Queue(maxsize=16)

    def wait_for_detection(self) -> None:
        """Block until the wake word is detected above the threshold.

        Raises:
            WakeWordError: If the detector encounters an unrecoverable error
                while waiting.
        """
        if not self._running or self._model is None:
            raise WakeWordError(
                "Wake-word detector is not started. Call start() before waiting."
            )

        while self._running:
            try:
                frame = self._audio_queue.get(timeout=0.25)
            except queue.Empty:
                continue
            except Exception as exc:
                raise WakeWordError(f"Wake-word audio queue failure: {exc}") from exc

            try:
                prediction = self._model.predict(frame)
            except Exception as exc:
                raise WakeWordError(f"Wake-word model inference failed: {exc}") from exc

            score = _extract_peak_score(prediction)
            if score < self._threshold:
                continue

            now = time.monotonic()
            if now - self._last_detection_ts < self._cooldown:
                continue

            self._last_detection_ts = now
            logger.info("Wake word detected score=%.3f", score)
            return

        raise WakeWordError("Wake-word detector stopped before detection occurred.")

    def _audio_callback(
        self,
        indata: Any,
        frames: int,
        time_info: Any,
        status: Any,
    ) -> None:
        """Enqueue audio frames from the streaming callback for model inference."""
        del frames, time_info

        if status:
            logger.warning("Wake-word stream status=%s", status)

        payload = indata.copy() if hasattr(indata, "copy") else indata
        try:
            self._audio_queue.put_nowait(payload)
        except queue.Full:
            # Dropping stale frames avoids unbounded latency in detection loop.
            return


def _load_openwakeword_module() -> Any:
    """Import and return openWakeWord, raising WakeWordError on failure."""
    try:
        import openwakeword
    except ImportError as exc:
        raise WakeWordError(
            "openwakeword is not installed. Install requirements.txt dependencies."
        ) from exc
    return openwakeword


def _load_sounddevice_module() -> Any:
    """Import and return sounddevice, raising WakeWordError on failure."""
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise WakeWordError(
            "sounddevice is not installed. Install requirements.txt dependencies."
        ) from exc
    return sd


def _build_openwakeword_model(openwakeword: Any, model_path: str) -> Any:
    """Create an openWakeWord model using common constructor signatures."""
    model_factory: Callable[..., Any] = openwakeword.Model

    constructors: tuple[dict[str, Any], ...] = (
        {"wakeword_models": [model_path]},
        {"wakeword_model_paths": [model_path]},
        {"model_paths": [model_path]},
        {"model_path": model_path},
    )

    last_type_error: TypeError | None = None
    for kwargs in constructors:
        try:
            return model_factory(**kwargs)
        except TypeError as exc:
            last_type_error = exc
            continue

    if last_type_error is not None:
        raise WakeWordError(
            f"Failed to construct openWakeWord model for '{model_path}': "
            f"{last_type_error}"
        ) from last_type_error

    raise WakeWordError(f"Failed to construct openWakeWord model for '{model_path}'.")


def _extract_peak_score(prediction: Any) -> float:
    """Extract the highest scalar confidence score from model prediction output."""
    if isinstance(prediction, int | float):
        return float(prediction)

    if isinstance(prediction, dict):
        if not prediction:
            return 0.0
        return max(_extract_peak_score(value) for value in prediction.values())

    if isinstance(prediction, list | tuple):
        if not prediction:
            return 0.0
        return max(_extract_peak_score(value) for value in prediction)

    return 0.0
