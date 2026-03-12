"""scheduler node — proactive initiation entry point.

The scheduler is a separate graph entry point triggered by APScheduler in a
background thread inside main.py. It constructs a proactive_message and
routes directly to the orchestrator, bypassing listen and transcribe.

State inputs:  (none — this is the graph entry point for proactive turns)
State outputs: proactive_message, transcript=None, intent=None
Side effects:  May read config values and recent conversation summary.
Edges:         → orchestrator (always)

Configuration:
    orchestrator.proactive_enabled: bool   — master toggle
    orchestrator.proactive_schedule: str   — cron expression
    orchestrator.proactive_prompt: str     — instruction to the orchestrator
"""

from __future__ import annotations

from typing import Any

from langgraph.types import RunnableConfig

from core.state import GraphState
from core.utils import get_logger

logger = get_logger(__name__)


def scheduler(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    """Construct a proactive message to initiate a Renix-started conversation.

    Called by the APScheduler job configured in ``main.py``. Builds a
    ``proactive_message`` from the configured prompt and any available context
    (time of day, recent conversation summary). The orchestrator node uses
    this instead of a user transcript to generate a natural spoken message.

    Args:
        state: Current graph state (typically empty at proactive entry).
        config: LangGraph runnable config containing thread_id.

    Returns:
        Partial state dict containing ``proactive_message`` (str),
        ``transcript=None``, and ``intent=None``.

    Raises:
        ConfigError: Propagated to state["error"] if proactive config is absent.
    """
    # Implemented in step 13 — feat(core): graph nodes
    raise NotImplementedError("scheduler node implemented in step 13")
