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
from typing import Any

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
            raise ConfigError(
                f"Cannot create log directory '{log_path.parent}': {exc}"
            ) from exc

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
_config: dict[str, Any] | None = None


def load_config(config_path: str = "config/config.yaml") -> dict[str, Any]:
    """Load and validate the YAML configuration file.

    Also reads environment variables from a ``.env`` file at the project root
    if it exists, making secrets available as ``os.environ`` entries.

    The configuration is cached after the first call. Subsequent calls return
    the cached dict without re-reading from disk.

    Args:
        config_path: Path to ``config.yaml``, relative to CWD or absolute.

    Returns:
        The fully parsed configuration dictionary.

    Raises:
        ConfigError: If the file is missing, unreadable, contains invalid YAML,
            or fails required-field validation.
    """
    global _config
    if _config is not None:
        return _config

    # Load .env secrets into os.environ before anything else.
    _load_dotenv()

    resolved = Path(config_path)
    if not resolved.is_absolute():
        resolved = Path.cwd() / resolved

    if not resolved.exists():
        raise ConfigError(
            f"Configuration file not found: '{resolved}'. "
            "Create it from config/config.yaml."
        )

    try:
        import yaml  # type: ignore[import-untyped]
        with resolved.open("r", encoding="utf-8") as fh:
            raw: object = yaml.safe_load(fh)
    except OSError as exc:
        raise ConfigError(
            f"Cannot read configuration file '{resolved}': {exc}"
        ) from exc
    except Exception as exc:
        raise ConfigError(f"Invalid YAML in '{resolved}': {exc}") from exc

    if not isinstance(raw, dict):
        raise ConfigError(
            f"Configuration file '{resolved}' must be a YAML mapping, "
            f"got {type(raw).__name__}."
        )

    _validate_config(raw)
    _config = raw
    return _config


def get_config() -> dict[str, Any]:
    """Return the already-loaded configuration dictionary.

    Must be called after ``load_config()`` at application startup.

    Returns:
        The loaded config dict.

    Raises:
        ConfigError: If called before ``load_config()``.
    """
    if _config is None:
        raise ConfigError(
            "Configuration has not been loaded. Call load_config() first."
        )
    return _config


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

#: Top-level keys that must be present in config.yaml.
_REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = (
    "llm",
    "orchestrator",
    "stt",
    "tts",
    "wake_word",
    "memory",
    "audio",
    "logging",
)


def _validate_config(cfg: dict[str, Any]) -> None:
    """Assert that all required top-level sections are present.

    Args:
        cfg: Parsed YAML dict to validate.

    Raises:
        ConfigError: If any required top-level key is absent.
    """
    missing = [k for k in _REQUIRED_TOP_LEVEL_KEYS if k not in cfg]
    if missing:
        raise ConfigError(
            f"Configuration is missing required section(s): {', '.join(missing)}. "
            "Refer to config/config.yaml for the full schema."
        )

    # LLM section must provide base_url and model.
    llm = cfg.get("llm", {})
    for field in ("base_url", "model"):
        if not llm.get(field):
            raise ConfigError(
                f"'llm.{field}' is required in config.yaml but is missing or empty."
            )


def _load_dotenv(dotenv_path: str = ".env") -> None:
    """Load a ``.env`` file into ``os.environ`` if it exists.

    Uses python-dotenv when available. Silently skips if the file does not
    exist (not all environments require a .env file).

    Args:
        dotenv_path: Path to the .env file, relative to CWD or absolute.

    Raises:
        ConfigError: If the .env file exists but cannot be parsed.
    """
    resolved = Path(dotenv_path)
    if not resolved.is_absolute():
        resolved = Path.cwd() / resolved

    if not resolved.exists():
        return

    try:
        from dotenv import load_dotenv
        load_dotenv(resolved, override=False)
    except ImportError:
        # python-dotenv not installed; parse the file manually.
        _parse_dotenv_manually(resolved)
    except Exception as exc:
        raise ConfigError(f"Failed to load .env file '{resolved}': {exc}") from exc


def _parse_dotenv_manually(path: Path) -> None:
    """Minimal .env parser used when python-dotenv is not installed.

    Handles ``KEY=value`` and ``KEY="value"`` lines. Ignores comments and
    blank lines. Does NOT override existing environment variables.

    Args:
        path: Absolute path to the .env file.

    Raises:
        ConfigError: If the file cannot be read.
    """
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ConfigError(f"Cannot read .env file '{path}': {exc}") from exc

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, raw_value = line.partition("=")
        key = key.strip()
        value = raw_value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value
