"""Renix — entry point.

Loads configuration, initialises hardware, compiles the LangGraph pipeline,
starts the APScheduler background thread (for proactive turns), and enters
the listen loop.

Usage:
    python main.py              # Standard foreground mode
    python main.py --daemon     # Daemon mode (future — see docs/architecture.md)
"""

from __future__ import annotations

# Implemented in step 15 — feat(repo): main.py + startup
# Startup sequence:
#   1. load_config()
#   2. configure_logging()
#   3. discover_devices()
#   4. Instantiate I/O modules (detector, recorder, transcriber, speaker)
#   5. build_graph()
#   6. Start APScheduler if proactive_enabled
#   7. Enter graph.stream() / graph.invoke() listen loop


def main() -> None:
    """Renix application entry point.

    Raises:
        ConfigError: If configuration is missing or invalid.
        AudioError: If required audio devices cannot be found.
    """
    raise NotImplementedError("main() implemented in step 15")


if __name__ == "__main__":
    main()
