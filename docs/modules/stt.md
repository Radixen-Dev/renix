# stt.md — Speech-to-Text Module

> **Status:** Stub — to be completed in step 16 (`docs: full documentation pass`).

---

## Overview

The STT module wraps [faster-whisper](https://github.com/SYSTRAN/faster-whisper). `WhisperTranscriber` implements `Transcriber` from `core/interfaces.py`.

The `transcribe` node passes raw 16 kHz mono PCM bytes in and receives a transcript string out. After calling this, the node clears `state["audio_bytes"]` to `None`.

## Security Note

Transcribed content must **never** be logged at INFO level or above. DEBUG-level logging of transcripts is permitted but must be noted in the module doc.

## Configuration

```yaml
stt:
  model_size: "base"   # tiny | base | small | medium | large
  device: "cpu"        # cpu | cuda
  language: "en"       # BCP-47 language code; omit for auto-detection
```

### Step 7 Verification

- `WhisperTranscriber` now provides complete behavior in `modules/stt/transcriber.py`:
  - model loading in constructor with `TranscriptionError` wrapping
  - PCM16-byte to float32 waveform conversion for faster-whisper input
  - `transcribe()` returns joined segment text and handles empty input
  - transcripts are never logged at INFO level or above
- Unit coverage in `tests/unit/test_transcriber.py` verifies:
  - model initialization parameters
  - successful transcription aggregation
  - empty input handling
  - model-load and inference failure wrapping
  - invalid odd-length PCM input handling
