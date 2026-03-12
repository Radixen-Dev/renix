"""Unit tests for config loading and validation (core/utils.py).

Tests:
- load_config() parses a valid config.yaml correctly.
- load_config() raises ConfigError when the file is missing.
- load_config() raises ConfigError when required sections are absent.
- load_config() raises ConfigError on invalid YAML.
- load_config() raises ConfigError when llm.base_url is missing.
- get_config() raises ConfigError before load_config() is called.
- _parse_dotenv_manually() parses KEY=value pairs correctly.
- _load_dotenv() silently skips when .env is absent.
"""

from __future__ import annotations

import os
import textwrap
from collections.abc import Iterator
from pathlib import Path

import pytest

import core.utils as utils_module


def _reset_config() -> None:
    """Reset the module-level _config cache between tests."""
    utils_module._config = None  # type: ignore[attr-defined]
    utils_module._configured = False


@pytest.fixture(autouse=True)
def reset_state() -> Iterator[None]:
    """Ensure each test starts with a clean config/logging state."""
    _reset_config()
    yield
    _reset_config()


# ---------------------------------------------------------------------------
# load_config
# ---------------------------------------------------------------------------

MINIMAL_VALID_YAML = textwrap.dedent("""\
    llm:
      base_url: "http://localhost:1234/v1"
      model: "test-model"
    orchestrator:
      proactive_enabled: false
    stt:
      model_size: "base"
    tts:
      rate: 175
    wake_word:
      model_path: "hey_test"
    memory:
      long_term_enabled: false
    audio:
      input_device: null
    logging:
      level: "INFO"
""")


class TestLoadConfig:
    """Tests for utils.load_config()."""

    def test_returns_dict_for_valid_yaml(self, tmp_path: Path) -> None:
        """load_config() must return a dict when given a valid config file."""
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(MINIMAL_VALID_YAML, encoding="utf-8")
        result = utils_module.load_config(str(cfg_file))
        assert isinstance(result, dict)
        assert result["llm"]["model"] == "test-model"

    def test_caches_after_first_call(self, tmp_path: Path) -> None:
        """load_config() must return the same object on repeated calls."""
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(MINIMAL_VALID_YAML, encoding="utf-8")
        first = utils_module.load_config(str(cfg_file))
        second = utils_module.load_config(str(cfg_file))
        assert first is second

    def test_raises_config_error_when_file_missing(self, tmp_path: Path) -> None:
        """load_config() must raise ConfigError when the file does not exist."""
        with pytest.raises(utils_module.ConfigError, match="not found"):
            utils_module.load_config(str(tmp_path / "nonexistent.yaml"))

    def test_raises_config_error_on_invalid_yaml(self, tmp_path: Path) -> None:
        """load_config() must raise ConfigError when YAML is malformed."""
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(": : invalid: yaml: {[", encoding="utf-8")
        with pytest.raises(utils_module.ConfigError, match="Invalid YAML|not found"):
            utils_module.load_config(str(cfg_file))

    def test_raises_config_error_when_not_a_mapping(self, tmp_path: Path) -> None:
        """load_config() must raise ConfigError when YAML root is not a dict."""
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text("- item1\n- item2\n", encoding="utf-8")
        with pytest.raises(utils_module.ConfigError, match="mapping"):
            utils_module.load_config(str(cfg_file))

    def test_raises_config_error_for_missing_required_sections(
        self, tmp_path: Path
    ) -> None:
        """load_config() must raise ConfigError when required sections are absent."""
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text("llm:\n  base_url: x\n  model: y\n", encoding="utf-8")
        with pytest.raises(utils_module.ConfigError, match="missing required section"):
            utils_module.load_config(str(cfg_file))

    def test_raises_config_error_when_llm_base_url_missing(
        self, tmp_path: Path
    ) -> None:
        """load_config() must raise ConfigError when llm.base_url is absent."""
        yaml_no_url = MINIMAL_VALID_YAML.replace(
            '  base_url: "http://localhost:1234/v1"\n', ""
        )
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(yaml_no_url, encoding="utf-8")
        with pytest.raises(utils_module.ConfigError, match="llm.base_url"):
            utils_module.load_config(str(cfg_file))


# ---------------------------------------------------------------------------
# get_config
# ---------------------------------------------------------------------------

class TestGetConfig:
    """Tests for utils.get_config()."""

    def test_raises_before_load_config(self) -> None:
        """get_config() must raise ConfigError when called before load_config()."""
        with pytest.raises(utils_module.ConfigError, match="not been loaded"):
            utils_module.get_config()

    def test_returns_loaded_config(self, tmp_path: Path) -> None:
        """get_config() must return the same dict that load_config() returned."""
        cfg_file = tmp_path / "config.yaml"
        cfg_file.write_text(MINIMAL_VALID_YAML, encoding="utf-8")
        loaded = utils_module.load_config(str(cfg_file))
        assert utils_module.get_config() is loaded


# ---------------------------------------------------------------------------
# _parse_dotenv_manually
# ---------------------------------------------------------------------------

class TestParseDotenvManually:
    """Tests for utils._parse_dotenv_manually()."""

    def test_sets_env_var_from_plain_value(self, tmp_path: Path) -> None:
        """KEY=value lines must be added to os.environ."""
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_KEY_RENIX=hello\n", encoding="utf-8")
        os.environ.pop("TEST_KEY_RENIX", None)
        utils_module._parse_dotenv_manually(env_file)  # type: ignore[attr-defined]
        assert os.environ["TEST_KEY_RENIX"] == "hello"
        del os.environ["TEST_KEY_RENIX"]

    def test_strips_quotes_from_value(self, tmp_path: Path) -> None:
        """Values wrapped in quotes must have the quotes stripped."""
        env_file = tmp_path / ".env"
        env_file.write_text('TEST_QUOTED_RENIX="quoted_value"\n', encoding="utf-8")
        os.environ.pop("TEST_QUOTED_RENIX", None)
        utils_module._parse_dotenv_manually(env_file)  # type: ignore[attr-defined]
        assert os.environ["TEST_QUOTED_RENIX"] == "quoted_value"
        del os.environ["TEST_QUOTED_RENIX"]

    def test_ignores_comments(self, tmp_path: Path) -> None:
        """Lines starting with # must not be parsed as variables."""
        env_file = tmp_path / ".env"
        env_file.write_text("# THIS_SHOULD_NOT_SET=anything\n", encoding="utf-8")
        os.environ.pop("THIS_SHOULD_NOT_SET", None)
        utils_module._parse_dotenv_manually(env_file)  # type: ignore[attr-defined]
        assert "THIS_SHOULD_NOT_SET" not in os.environ

    def test_does_not_override_existing_env_var(self, tmp_path: Path) -> None:
        """Existing environment variables must not be overridden."""
        env_file = tmp_path / ".env"
        env_file.write_text("TEST_EXISTING_RENIX=new_value\n", encoding="utf-8")
        os.environ["TEST_EXISTING_RENIX"] = "original"
        utils_module._parse_dotenv_manually(env_file)  # type: ignore[attr-defined]
        assert os.environ["TEST_EXISTING_RENIX"] == "original"
        del os.environ["TEST_EXISTING_RENIX"]


# ---------------------------------------------------------------------------
# _load_dotenv
# ---------------------------------------------------------------------------

class TestLoadDotenv:
    """Tests for utils._load_dotenv()."""

    def test_silently_skips_when_dotenv_absent(self, tmp_path: Path) -> None:
        """_load_dotenv() must not raise when .env file does not exist."""
        utils_module._load_dotenv(str(tmp_path / "nonexistent.env"))  # type: ignore[attr-defined]
