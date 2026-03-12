"""transcribe node — calls the STT module, writes transcript to state.

State inputs:  audio_bytes
State outputs: transcript, audio_bytes=None
Side effects:  Calls Transcriber.transcribe(audio_bytes).
               Clears audio_bytes to prevent persistence in MemorySaver.
Edges:         → orchestrator (always)
"""

from __future__ import annotations

from typing import Any

from langgraph.types import RunnableConfig

from core.state import GraphState
from core.utils import get_logger

logger = get_logger(__name__)


def transcribe(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    """Transcribe raw PCM audio from state to text.

    Reads ``audio_bytes`` from state, passes it to the configured STT module,
    writes the resulting transcript string back, and **must** clear
    ``audio_bytes`` to ``None`` so it is never persisted to MemorySaver.

    Args:
        state: Current graph state. Reads ``audio_bytes``.
        config: LangGraph runnable config.

    Returns:
        Partial state dict containing ``transcript`` (str) and
        ``audio_bytes=None``.

    Raises:
        TranscriptionError: Propagated to state["error"] if STT fails.
    """
    # Implemented in step 13 — feat(core): graph nodes
    raise NotImplementedError("transcribe node implemented in step 13")
