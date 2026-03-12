"""Tool registry — converts ToolPlugin instances to LangChain tool callables.

Called once at startup by the ``tool_use_agent`` to build the list of
LangChain tools bound to its internal ``ToolNode``.
"""

from __future__ import annotations

from langchain_core.tools import BaseTool

from core.interfaces import ToolPlugin
from core.utils import get_logger

logger = get_logger(__name__)


def build_langchain_tools(plugins: list[ToolPlugin]) -> list[BaseTool]:
    """Convert a list of ToolPlugin instances to LangChain BaseTool objects.

    Each plugin's ``run`` method is wrapped in a LangChain ``@tool``-decorated
    callable. The plugin's ``name`` and ``description`` are used to generate
    the tool schema passed to the LLM.

    Args:
        plugins: List of ``ToolPlugin`` instances from ``modules/tools/__init__.py``.

    Returns:
        List of LangChain ``BaseTool`` objects ready for a ``ToolNode``.

    Raises:
        ToolError: If any plugin fails validation or schema generation.
    """
    # Implemented in step 9 — feat(tools): registry + builtins
    raise NotImplementedError("build_langchain_tools implemented in step 9")
