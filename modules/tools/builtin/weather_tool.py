"""Weather tool — fetches current weather for a given location.

Requires ``WEATHER_API_KEY`` in ``.env``. The API endpoint is configured in
``config.yaml`` under ``tools.weather.base_url``. No hardcoded URLs here.
"""

from __future__ import annotations

import json
import os
from urllib import parse, request

from core.interfaces import ToolPlugin
from core.utils import ToolError, get_config, get_logger, load_config

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
        location = str(kwargs.get("location", "")).strip()
        if not location:
            raise ToolError(
                "Weather tool requires a non-empty 'location' argument."
            )

        api_key = os.getenv("WEATHER_API_KEY", "").strip()
        if not api_key:
            raise ToolError(
                "WEATHER_API_KEY is missing. Add it to your .env file."
            )

        base_url = self._resolve_base_url()
        url = self._build_url(base_url=base_url, location=location, api_key=api_key)
        payload = self._fetch_json(url)
        return self._format_weather(payload)

    def _resolve_base_url(self) -> str:
        """Resolve weather API base URL from loaded config or config file."""
        try:
            cfg = get_config()
        except Exception:
            cfg = load_config()

        base_url = (
            cfg.get("tools", {}).get("weather", {}).get("base_url", "")
            if isinstance(cfg, dict)
            else ""
        )
        if not isinstance(base_url, str) or not base_url.strip():
            raise ToolError(
                "tools.weather.base_url is missing from config/config.yaml."
            )
        return base_url.rstrip("/")

    def _build_url(self, base_url: str, location: str, api_key: str) -> str:
        """Build OpenWeatherMap current weather URL."""
        query = parse.urlencode(
            {
                "q": location,
                "appid": api_key,
                "units": "metric",
            }
        )
        return f"{base_url}/weather?{query}"

    def _fetch_json(self, url: str) -> dict[str, object]:
        """Fetch weather JSON payload from API endpoint."""
        req = request.Request(
            url,
            headers={"Accept": "application/json"},
            method="GET",
        )
        try:
            with request.urlopen(req, timeout=10) as resp:
                raw = resp.read().decode("utf-8", errors="replace")
        except Exception as exc:
            raise ToolError(f"Weather request failed: {exc}") from exc

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ToolError(f"Weather API returned invalid JSON: {exc}") from exc

        if not isinstance(payload, dict):
            raise ToolError("Weather API returned unexpected payload shape.")
        return payload

    def _format_weather(self, payload: dict[str, object]) -> str:
        """Format OpenWeatherMap payload to a concise weather summary."""
        city = str(payload.get("name", "Unknown location"))

        main = payload.get("main")
        temp = None
        if isinstance(main, dict):
            temp_value = main.get("temp")
            if isinstance(temp_value, int | float):
                temp = float(temp_value)

        weather = payload.get("weather")
        description = "unknown conditions"
        if isinstance(weather, list) and weather:
            first = weather[0]
            if isinstance(first, dict):
                desc = first.get("description")
                if isinstance(desc, str) and desc.strip():
                    description = desc.strip()

        wind = payload.get("wind")
        wind_speed = None
        if isinstance(wind, dict):
            speed = wind.get("speed")
            if isinstance(speed, int | float):
                wind_speed = float(speed)

        parts = [f"{city}:"]
        if temp is not None:
            parts.append(f"{temp:.0f}°C")
        parts.append(description)
        if wind_speed is not None:
            parts.append(f"wind {wind_speed:.0f} m/s")
        return ", ".join(parts)
