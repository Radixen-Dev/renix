"""Shared utilities for Renix — logging factory, config loader, and exceptions.

All submodule-specific exceptions inherit from ``RenixError``. The logger
factory produces consistently formatted loggers that respect the configured
log level from ``config.yaml``.
"""

from __future__ import annotations

import logging
import logging.handlers
import os
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    pass

# ---------------------------------------------------------------------------
# Exception hierarchy
# ---------------------------------------------------------------------------


class RenixError(Exception):
    """Base exception for all Renix-internal errors.

    Catch this at the graph boundary to surface structured errors to state.
    Always includes a human-readable message suitable for ``state["error"]``.
    """


class ConfigError(RenixError):
    """Raised when configuration is missing, malformed, or invalid."""


class AudioError(RenixError):
    """Raised when audio device access or recording fails."""


class WakeWordError(RenixError):
    """Raised when the wake-word detection engine fails."""


class TranscriptionError(RenixError):
    """Raised when the STT model fails to process audio."""


class LLMError(RenixError):
    """Raised when the LLM API call fails or returns an unexpected result."""


class TTSError(RenixError):
    """Raised when the TTS engine fails to produce or play audio."""


class ToolError(RenixError):
    """Raised when a tool plugin execution fails."""


class AgentError(RenixError):
    """Raised when a subagent subgraph fails to build or execute."""


# ---------------------------------------------------------------------------
# Logging factory
# ---------------------------------------------------------------------------

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
_configured = False


def get_logger(name: str) -> logging.Logger:
    """Return a named logger, configuring the root logger on first call.

    Configuration (level, file handler) is read from the loaded config dict
    if ``configure_logging`` has been called; otherwise INFO level is used.

    Args:
        name: Dotted logger name, typically ``__name__`` of the calling module.

    Returns:
        A ``logging.Logger`` instance ready for use.
    """
    return logging.getLogger(name)


def configure_logging(
    level: str = "INFO",
    log_to_file: bool = False,
    log_file: str = "logs/renix.log",
) -> None:
    """Configure the root logger from resolved config values.

    Should be called once at application startup in ``main.py`` after the
    config is loaded. Subsequent calls to ``get_logger`` will inherit this
    configuration.

    Args:
        level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_to_file: Whether to add a rotating file handler.
        log_file: Path to the log file, relative to the project root.

    Raises:
        ConfigError: If the log file directory cannot be created.
    """
    global _configured
    if _configured:
        return

    numeric_level = getattr(logging, level.upper(), logging.INFO)
    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)

    root = logging.getLogger()
    root.setLevel(numeric_level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root.addHandler(console_handler)

    if log_to_file:
        log_path = Path(log_file)
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            raise ConfigError(f"Cannot create log directory '{log_path.parent}': {exc}") from exc

        file_handler = logging.handlers.RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    _configured = True


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

# Populated by load_config(); accessed project-wide via get_config().
_config: Optional[dict[str, Any]] = None


def load_config(config_path: str = "config/config.yaml") -> dict[str, Any]:
    """Load and validate the YAML configuration file.

    Also reads environment variables from a ``.env`` file if present, making
    secrets available as ``os.environ`` entries.

    Args:
        config_path: Path to ``config.yaml``, relative to project root or absolute.

    Returns:
        The fully parsed configuration dictionary.

    Raises:
        ConfigError: If the file is missing, unreadable, or fails schema
            validation.
    """
    # Implemented in step 2 — feat(config): config loading and validation
    raise NotImplementedError("load_config implemented in step 2")


def get_config() -> dict[str, Any]:
    """Return the already-loaded configuration dictionary.

    Must be called after ``load_config()`` at startup.

    Returns:
        The loaded config dict.

    Raises:
        ConfigError: If called before ``load_config()``.
    """
    if _config is None:
        raise ConfigError("Configuration has not been loaded. Call load_config() first.")
    return _config
