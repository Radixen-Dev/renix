# wake_word.md — Wake Word Module

> **Status:** Stub — to be completed in step 16 (`docs: full documentation pass`).

---

## Overview

The wake-word module wraps [openWakeWord](https://github.com/dscripka/openWakeWord). `OpenWakeWordDetector` implements `WakeWordDetector` from `core/interfaces.py`.

The `listen` node calls `wait_for_detection()` which blocks until the model fires above the configured threshold.

## Configuration

```yaml
wake_word:
  model_path: "hey_renix"   # Built-in model name or path to custom .onnx model
  threshold: 0.5            # Confidence score 0.0–1.0
  cooldown_seconds: 2       # Minimum gap between detections
```
