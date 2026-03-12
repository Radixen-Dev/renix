"""Audio device autodiscovery and validation.

This is the ONLY file in the project that contains platform-specific logic.
All differences between Raspberry Pi OS (ARM) and Windows 10/11 are handled
here. The rest of the codebase is platform-agnostic.

Responsibilities:
- Enumerate available input and output audio devices.
- Resolve device names/indices from config.yaml (or fall back to system defaults).
- Validate that the resolved devices are capable of the required sample rate.
- Expose a single DeviceConfig dataclass consumed by recorder.py and speaker.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from core.utils import AudioError, get_logger

logger = get_logger(__name__)


@dataclass
class DeviceConfig:
    """Resolved audio device configuration.

    Attributes:
        input_device: sounddevice device index for the microphone, or ``None``
            to use the system default.
        output_device: sounddevice device index for the speaker, or ``None``
            to use the system default.
        sample_rate: Target sample rate in Hz (default 16000).
        chunk_size: Frames per buffer chunk (default 1024).
    """

    input_device: int | None
    output_device: int | None
    sample_rate: int = 16000
    chunk_size: int = 1024


def discover_devices(
    input_device: str | int | None = None,
    output_device: str | int | None = None,
    sample_rate: int = 16000,
    chunk_size: int = 1024,
) -> DeviceConfig:
    """Autodiscover and validate audio input/output devices.

    Resolves device names or indices from config values. Falls back to the
    system default if ``None`` is provided. Validates that the resolved
    devices support the requested sample rate.

    Args:
        input_device: Device name substring, integer index, or ``None`` for
            the system default.
        output_device: Device name substring, integer index, or ``None`` for
            the system default.
        sample_rate: Required sample rate in Hz.
        chunk_size: Frames per recording chunk.

    Returns:
        A ``DeviceConfig`` with resolved integer device indices.

    Raises:
        AudioError: If a specified device cannot be found or does not support
            the requested sample rate.
    """
    if sample_rate <= 0:
        raise AudioError(f"Invalid sample_rate '{sample_rate}'. Must be > 0.")
    if chunk_size <= 0:
        raise AudioError(f"Invalid chunk_size '{chunk_size}'. Must be > 0.")

    sd = _load_sounddevice_module()
    devices = _query_devices(sd)

    resolved_input = _resolve_device_index(sd, devices, input_device, "input")
    resolved_output = _resolve_device_index(sd, devices, output_device, "output")

    if resolved_input is not None:
        _validate_device_sample_rate(sd, resolved_input, sample_rate, "input")
    if resolved_output is not None:
        _validate_device_sample_rate(sd, resolved_output, sample_rate, "output")

    return DeviceConfig(
        input_device=resolved_input,
        output_device=resolved_output,
        sample_rate=sample_rate,
        chunk_size=chunk_size,
    )


def _load_sounddevice_module() -> Any:
    """Import and return the sounddevice module.

    Raises:
        AudioError: If sounddevice is not available in the runtime environment.
    """
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise AudioError(
            "sounddevice is not installed. Install requirements.txt dependencies."
        ) from exc
    return sd


def _query_devices(sd: Any) -> list[dict[str, Any]]:
    """Return the full sounddevice device list normalized to dict entries."""
    try:
        raw = sd.query_devices()
    except Exception as exc:
        raise AudioError(f"Failed to query audio devices: {exc}") from exc

    devices: list[dict[str, Any]] = []
    for entry in raw:
        devices.append(dict(entry))
    return devices


def _resolve_device_index(
    sd: Any,
    devices: list[dict[str, Any]],
    spec: str | int | None,
    kind: Literal["input", "output"],
) -> int | None:
    """Resolve a config device selector to a concrete sounddevice index."""
    if spec is None:
        return _resolve_default_index(sd, devices, kind)

    if isinstance(spec, int):
        _ensure_device_index_valid(devices, spec, kind)
        return spec

    needle = spec.strip().lower()
    if not needle:
        return _resolve_default_index(sd, devices, kind)

    for idx, dev in enumerate(devices):
        name = str(dev.get("name", "")).lower()
        if needle in name and _device_supports_kind(dev, kind):
            return idx

    raise AudioError(
        f"No {kind} audio device matching '{spec}' was found. "
        "Check config.audio settings or use null for system default."
    )


def _resolve_default_index(
    sd: Any,
    devices: list[dict[str, Any]],
    kind: Literal["input", "output"],
) -> int | None:
    """Resolve system default index, falling back to first compatible device."""
    default_pair = getattr(sd.default, "device", None)
    if isinstance(default_pair, list | tuple) and len(default_pair) >= 2:
        candidate = default_pair[0] if kind == "input" else default_pair[1]
        if isinstance(candidate, int) and candidate >= 0:
            _ensure_device_index_valid(devices, candidate, kind)
            return candidate

    for idx, dev in enumerate(devices):
        if _device_supports_kind(dev, kind):
            return idx
    return None


def _ensure_device_index_valid(
    devices: list[dict[str, Any]],
    index: int,
    kind: Literal["input", "output"],
) -> None:
    """Validate that an index exists and supports the requested direction."""
    if index < 0 or index >= len(devices):
        raise AudioError(
            f"{kind.capitalize()} device index {index} is out of range "
            f"(0..{len(devices) - 1})."
        )

    dev = devices[index]
    if not _device_supports_kind(dev, kind):
        raise AudioError(
            f"Device index {index} does not support {kind} channels."
        )


def _device_supports_kind(
    dev: dict[str, Any], kind: Literal["input", "output"]
) -> bool:
    """Return whether a device exposes at least one channel for the given kind."""
    if kind == "input":
        return int(dev.get("max_input_channels", 0) or 0) > 0
    return int(dev.get("max_output_channels", 0) or 0) > 0


def _validate_device_sample_rate(
    sd: Any,
    index: int,
    sample_rate: int,
    kind: Literal["input", "output"],
) -> None:
    """Validate that a device supports the requested sample rate."""
    try:
        if kind == "input":
            sd.check_input_settings(
                device=index,
                samplerate=sample_rate,
                channels=1,
            )
        else:
            sd.check_output_settings(
                device=index,
                samplerate=sample_rate,
                channels=1,
            )
    except Exception as exc:
        raise AudioError(
            f"{kind.capitalize()} device index {index} does not support "
            f"{sample_rate}Hz mono audio: {exc}"
        ) from exc
