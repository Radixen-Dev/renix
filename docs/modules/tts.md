# tts.md — Text-to-Speech Module

> **Status:** Stub — to be completed in step 16 (`docs: full documentation pass`).

---

## Overview

The TTS module wraps [pyttsx3](https://pyttsx3.readthedocs.io/). `Pyttsx3Speaker` implements `Speaker` from `core/interfaces.py`.

The `respond` node passes `state["response"]` to `Speaker.speak()`. This is a side-effect-only call; nothing is written back to state.

## Swapping TTS Engines

To swap pyttsx3 for a different TTS engine:

1. Create a new class implementing `Speaker` in `modules/tts/`.
2. Update `main.py` to instantiate the new class.
3. Update config as needed.

No graph or node changes required.

## Configuration

```yaml
tts:
  rate: 175          # Words per minute
  volume: 1.0        # 0.0–1.0
  voice_id: null     # null = system default, or platform voice ID string
```
