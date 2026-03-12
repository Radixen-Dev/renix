# tools.md — Tool Plugin System

> **Status:** Stub — to be completed in step 16 (`docs: full documentation pass`).

---

## Overview

Tools implement `ToolPlugin` from `core/interfaces.py`. They are registered in `modules/tools/__init__.py` and converted to LangChain `BaseTool` objects by `modules/tools/registry.py`. The `tool_use_agent` subgraph binds the converted tools to a `ToolNode`.

---

## How to Add a Tool

1. Create `modules/tools/builtin/my_tool.py` implementing `ToolPlugin`.
2. Add an instance to `TOOLS` in `modules/tools/__init__.py`.
3. Add a section to this file with: name, description, parameters, return value, configuration required.

**No other files change.**

---

## Built-in Tools

### TimeTool

- **Name:** `get_current_time`
- **Description:** Returns the current local date and time.
- **Parameters:** None.
- **Returns:** Formatted datetime string.
- **Configuration:** None required.

### WeatherTool

- **Name:** `get_weather`
- **Description:** Fetches current weather for a given location.
- **Parameters:** `location` (str) — city name or location string.
- **Returns:** Plain-text weather summary.
- **Configuration:** `WEATHER_API_KEY` in `.env`; base URL in `config.yaml` under `tools.weather.base_url`.
