"""orchestrator node — sole user-facing LLM node.

The orchestrator is the only node that generates text the user hears. It
reads context from state, calls the LLM, and either delegates to a subagent
(by setting intent) or produces a final spoken response (by setting response).

State inputs:  messages, transcript, proactive_message, error, active_subagent
State outputs: messages (appended), intent OR response, active_subagent=None
Side effects:  One LLM API call per invocation (ChatOpenAI → OpenAI-compat endpoint).
Edges:         → route     (when intent is set — subagent delegation)
               → respond   (when response is set — final answer ready)

Security notes:
- Audio content and transcripts are NEVER logged at INFO or above.
- LLM responses are NEVER logged at INFO or above.
- The system prompt explicitly instructs the model not to reveal subagents.
"""

from __future__ import annotations

from typing import Any

from langchain_core.runnables import RunnableConfig

from core.state import GraphState
from core.utils import get_logger

logger = get_logger(__name__)


def orchestrator(state: GraphState, config: RunnableConfig) -> dict[str, Any]:
    """Generate the next LLM response or delegate to a subagent.

    Reads the accumulated message history, current transcript (or proactive
    message), and any error condition. Calls the configured LLM and interprets
    the result:

    - If the response signals subagent delegation: sets ``intent``, does NOT
      set ``response``. The conditional edge routes to ``route``.
    - If the response is a final answer: sets ``response``, clears ``intent``.
      The conditional edge routes to ``respond``.

    Args:
        state: Current graph state.
        config: LangGraph runnable config containing thread_id.

    Returns:
        Partial state dict. Always contains an updated ``messages`` list.
        Contains either ``intent`` (str) or ``response`` (str), never both.

    Raises:
        LLMError: Propagated to state["error"] if the API call fails.
    """
    # Implemented in step 13 — feat(core): graph nodes
    raise NotImplementedError("orchestrator node implemented in step 13")
