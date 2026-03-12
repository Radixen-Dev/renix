"""Weather tool — fetches current weather for a given location.

Requires ``WEATHER_API_KEY`` in ``.env``. The API endpoint is configured in
``config.yaml`` under ``tools.weather.base_url``. No hardcoded URLs here.
"""

from __future__ import annotations

from core.interfaces import ToolPlugin
from core.utils import get_logger

logger = get_logger(__name__)


class WeatherTool(ToolPlugin):
    """Fetches current weather conditions for a specified location.

    Reads the API key from the environment and the base URL from config.
    Never logs the API key or raw API response at INFO level or above.

    Attributes:
        name: ``"get_weather"``
        description: LLM-facing description used to generate the tool schema.
    """

    name = "get_weather"
    description = (
        "Fetches the current weather for a given city or location. "
        "Use this when the user asks about weather conditions."
    )

    def run(self, **kwargs: object) -> str:
        """Fetch current weather for the specified location.

        Args:
            **kwargs: Tool arguments. Uses optional ``location`` key for the
                target city/location string (e.g. ``"London, UK"``).

        Returns:
            Plain-text weather summary, e.g.
            ``"London: 12°C, partly cloudy, wind 15 km/h NW."``.

        Raises:
            ToolError: If the API key is missing, the request fails, or the
                response cannot be parsed.
        """
        _location = str(kwargs.get("location", ""))
        # Implemented in step 9 — feat(tools): registry + builtins
        raise NotImplementedError("WeatherTool.run implemented in step 9")
