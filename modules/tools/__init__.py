"""Tool plugin registry — all ToolPlugin instances registered here.

To add a new tool:
1. Create ``modules/tools/builtin/my_tool.py`` implementing ``ToolPlugin``.
2. Import it and add an instance to ``TOOLS`` below.
3. Document it in ``docs/modules/tools.md``.
No other files change.
"""

from __future__ import annotations

from core.interfaces import ToolPlugin
from modules.tools.builtin.time_tool import TimeTool
from modules.tools.builtin.weather_tool import WeatherTool

TOOLS: list[ToolPlugin] = [
    TimeTool(),
    WeatherTool(),
]
