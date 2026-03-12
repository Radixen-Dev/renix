"""respond node — calls TTS with the final response from state.

State inputs:  response
State outputs: (none — side effect only)
Side effects:  Calls Speaker.speak(response) to play audio through the
               configured output device.
Edges:         → listen (always — completes the turn loop)
"""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableConfig

from core.state import GraphState
from core.utils import get_logger

logger = get_logger(__name__)


def respond(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    """Speak the final response aloud via the configured TTS module.

    Reads ``state["response"]`` and passes it to the Speaker. Returns an
    empty dict — all state changes for this turn are already complete.

    Args:
        state: Current graph state. Reads ``response``.
        config: LangGraph runnable config.

    Returns:
        Empty dict (no state mutations — this node is a pure side-effect call).

    Raises:
        TTSError: Propagated to state["error"] if TTS playback fails.
    """
    # Implemented in step 13 — feat(core): graph nodes
    raise NotImplementedError("respond node implemented in step 13")
