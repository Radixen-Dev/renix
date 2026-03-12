# audio.md — Audio Module

> **Status:** Stub — to be completed in step 16 (`docs: full documentation pass`).

---

## Overview

The audio module handles device autodiscovery and microphone recording. It is the **only** place in the project with platform-specific logic (Windows vs. Raspberry Pi OS ARM).

## device_manager.py

`discover_devices()` resolves device indices from config values (name string, integer index, or `null` for system default), validates that the device supports the required sample rate, and returns a `DeviceConfig` dataclass.

## recorder.py

`SoundDeviceRecorder` implements `AudioRecorder`. Called by the `listen` node after wake-word detection. Returns raw 16 kHz mono PCM bytes.

## Configuration

```yaml
audio:
  input_device: null    # null = system default
  output_device: null
  sample_rate: 16000
  chunk_size: 1024
```
