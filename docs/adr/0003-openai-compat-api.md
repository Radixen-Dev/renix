# ADR-0003: OpenAI-Compatible API Format

**Date:** 2026-03-12  
**Status:** Accepted

## Context

Renix targets locally-running LLMs (e.g. via LM Studio, Ollama, llama.cpp server) as well as optional cloud endpoints. Each LLM provider and local inference framework historically exposed a different SDK or REST API shape, requiring provider-specific integration code.

LangChain's `ChatOpenAI` class supports pointing to any OpenAI-compatible endpoint via `base_url`, making it the lowest-coupling integration point available.

## Decision

Use LangChain's `ChatOpenAI` pointed at a configurable `base_url` for all LLM calls. The endpoint, model name, and API key are all in `config.yaml` / `.env`. No model-specific SDKs (Anthropic, Cohere, HuggingFace, Ollama-native, etc.) are used in v0.1.

## Consequences

**Easier:**
- Any OpenAI-compatible local server (LM Studio, Ollama's OpenAI compat layer, vLLM, llama.cpp server) works without code changes.
- Switching models or providers requires only a `config.yaml` change.
- One integration path in the codebase — no conditional logic per provider.

**Harder:**
- Provider-specific features (function calling format differences, vision, audio input) may require additional abstraction if a non-compatible model is needed in the future.
- If a model only exposes a non-OpenAI-compatible API natively, an adapter layer or different `ChatModel` class must be introduced — this would require a new ADR.
