"""Parent StateGraph — builds and compiles the Renix LangGraph pipeline.

This module is the single place where all nodes are wired together, conditional
edges are defined, subagent subgraphs are registered, and ``MemorySaver`` is
attached. The compiled graph is returned to ``main.py`` and never re-compiled.

Graph topology:
    Reactive:   __start__ → listen → transcribe → orchestrator → route →
                [subagent] → orchestrator → respond → listen
    Proactive:  __start__ → scheduler → orchestrator → respond → listen

Rules:
- This file imports from ``core/nodes/`` and ``modules/agents/`` only.
- Never add a node here without a corresponding entry in docs/architecture.md.
- The graph is compiled once; ``main.py`` reuses the compiled object.
"""

from __future__ import annotations

# Implemented in step 14 — feat(core): parent graph
# All wiring, conditional edges, MemorySaver attachment, and subagent
# registration happen here.

from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph

from core.state import GraphState
from core.utils import get_logger

logger = get_logger(__name__)


def build_graph() -> Any:
    """Build, compile, and return the parent Renix StateGraph.

    Registers all nodes, defines all edges (including conditional edges),
    attaches subagent subgraphs, and compiles with ``MemorySaver``.

    Returns:
        A compiled LangGraph ``CompiledGraph`` ready for ``graph.invoke()``.

    Raises:
        AgentError: If any subagent subgraph fails to build.
        ConfigError: If required configuration values are missing.
    """
    # Implemented in step 14 — feat(core): parent graph
    raise NotImplementedError("build_graph implemented in step 14")
