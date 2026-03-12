"""Time tool — returns the current local date and time.

A simple built-in tool that requires no external API calls or secrets.
"""

from __future__ import annotations

from datetime import datetime

from core.interfaces import ToolPlugin
from core.utils import get_logger

logger = get_logger(__name__)


class TimeTool(ToolPlugin):
    """Returns the current local date and time as a formatted string.

    No configuration required. Safe to call on any platform.

    Attributes:
        name: ``"get_current_time"``
        description: LLM-facing description used to generate the tool schema.
    """

    name = "get_current_time"
    description = (
        "Returns the current local date and time. "
        "Use this when the user asks what time or date it is."
    )

    def run(self, **kwargs: object) -> str:
        """Return the current local date and time as a human-readable string.

        Args:
            **kwargs: Ignored — this tool takes no parameters.

        Returns:
            Current local datetime string, e.g. ``"Wednesday, 12 March 2026, 14:35"``.
        """
        del kwargs
        now = datetime.now().astimezone()
        return now.strftime("%A, %d %B %Y, %H:%M %Z")
