"""GraphState — the single shared state schema for the Renix LangGraph pipeline.

Every node reads from and writes partial updates to this TypedDict.
No code outside a node function may create or modify state.
"""

from __future__ import annotations

from typing import Annotated

from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class GraphState(TypedDict):
    """Single source of truth for one conversation turn.

    Fields are updated exclusively by node functions via partial-dict returns.
    Mutating this object directly anywhere outside a node is a hard violation.

    Attributes:
        messages: Full LangChain message history. Uses ``add_messages`` reducer
            so nodes append new messages rather than replacing the list.
        transcript: Current user utterance, populated by the ``transcribe`` node.
            Reset to ``None`` at the start of each turn by ``listen``.
        response: Final text to be spoken, populated by the ``orchestrator`` node.
            Reset to ``None`` at the start of each turn by ``listen``.
        intent: Classified intent label set by the ``route`` node to dispatch a
            subagent. Cleared when the orchestrator produces a final response.
        active_subagent: Name of the subagent currently executing, or ``None``.
        audio_bytes: Raw 16 kHz mono PCM audio captured by the recorder.
            **Must** be set to ``None`` by ``transcribe`` after use; never
            persisted to MemorySaver.
        proactive_message: Set by the ``scheduler`` node to trigger a
            Renix-initiated turn, bypassing ``listen`` and ``transcribe``.
        error: Last error message string. The ``orchestrator`` reads this on
            entry to decide whether to surface the error to the user.
    """

    # Conversation
    messages: Annotated[
        list[object], add_messages
    ]  # full message history (LangChain messages)
    transcript: str | None  # current user utterance, set by transcribe
    response: str | None  # final text to speak, set by orchestrator

    # Routing
    intent: str | None  # classified intent label, set by route
    active_subagent: str | None  # name of subagent currently executing

    # Audio
    audio_bytes: bytes | None  # raw PCM from recorder — CLEARED after STT

    # Proactive initiation
    proactive_message: str | None  # set by scheduler to bypass listen/transcribe

    # Error propagation
    error: str | None  # last error message; orchestrator reads this
