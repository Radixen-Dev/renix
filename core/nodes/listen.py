"""listen node — awaits wake word then records audio into state.

State inputs:  (none — resets transcript/response at turn start)
State outputs: audio_bytes, transcript=None, response=None
Side effects:  Blocks on WakeWordDetector.wait_for_detection(), calls
               AudioRecorder.record() to capture microphone audio.
Edges:         → transcribe (always)
"""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableConfig

from core.state import GraphState
from core.utils import get_logger

logger = get_logger(__name__)


def listen(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    """Block until the wake word is detected, then record one utterance.

    Resets ``transcript`` and ``response`` to ``None`` to begin a clean turn,
    then blocks on the wake-word detector. Once triggered, records audio and
    writes the raw PCM bytes to state.

    Args:
        state: Current graph state (fields read: none beyond reset targets).
        config: LangGraph runnable config (thread_id, etc.).

    Returns:
        Partial state dict containing ``audio_bytes``, ``transcript=None``,
        and ``response=None``.

    Raises:
        WakeWordError: Propagated to state["error"] if detection fails.
        AudioError: Propagated to state["error"] if recording fails.
    """
    # Implemented in step 13 — feat(core): graph nodes
    raise NotImplementedError("listen node implemented in step 13")
