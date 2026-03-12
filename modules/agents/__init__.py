"""Subagent plugin registry — all SubagentPlugin instances registered here.

To add a new subagent:
1. Create ``modules/agents/my_agent.py`` implementing ``SubagentPlugin``.
2. Import it and add an instance to ``AGENTS`` below.
3. Add the intent label(s) to the dispatch table in ``core/nodes/route.py``.
4. Document it in ``docs/modules/agents.md``.
No other files change.
"""

from __future__ import annotations

from core.interfaces import SubagentPlugin
from modules.agents.mcp_agent import MCPAgent
from modules.agents.memory_agent import MemoryAgent
from modules.agents.tool_use_agent import ToolUseAgent

AGENTS: list[SubagentPlugin] = [
    ToolUseAgent(),
    MemoryAgent(),
    MCPAgent(),
]
