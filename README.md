# Renix

**Renix** is a locally-running, modular AI voice assistant orchestrated by [LangGraph](https://github.com/langchain-ai/langgraph). It listens for a wake word, transcribes speech, routes the turn through a compiled LangGraph agent graph, and speaks the response — all with a plugin architecture that allows new agents and tools to be added without modifying any existing code.

Developed by **Radixen**.

---

## Features

- **Wake-word triggered** — powered by openWakeWord.
- **Local STT** — faster-whisper running fully on-device (CPU or CUDA).
- **Local TTS** — pyttsx3 with configurable voice, rate, and volume.
- **LangGraph orchestration** — compiled `StateGraph` with `MemorySaver` for turn-to-turn conversation memory.
- **Plugin architecture** — add tools and subagents without touching the graph.
- **Proactive turns** — Renix can initiate conversations via APScheduler.
- **Cross-platform** — Raspberry Pi OS (Bookworm 64-bit ARM) and Windows 10/11.
- **OpenAI-compatible LLM** — works with any local or remote server exposing the OpenAI API format.

---

## Requirements

- Python 3.11+
- A running OpenAI-compatible LLM endpoint (e.g. [LM Studio](https://lmstudio.ai/))

## Installation

```bash
git clone https://github.com/radixen/renix.git
cd renix
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / Raspberry Pi
pip install -r requirements.txt
cp config/.env.example .env   # fill in any API keys
```

## Configuration

Edit `config/config.yaml` to configure the LLM endpoint, STT model, TTS voice, wake word, audio devices, and more.

Secret API keys go in `.env` only — see `config/.env.example`.

## Running

```bash
python main.py
```

## Development

```bash
pip install -r requirements-dev.txt
pytest                  # run tests
ruff check .            # lint
mypy .                  # type check
```

See [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) for branch, commit, and PR rules.

---

## Documentation

| Document | Description |
|---|---|
| [docs/architecture.md](docs/architecture.md) | Full system diagram, node index, extension guide |
| [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) | Human contributor rules |
| [docs/AGENTS.md](docs/AGENTS.md) | AI agent contributor rules |
| [docs/modules/](docs/modules/) | Per-module documentation |
| [docs/adr/](docs/adr/) | Architecture decision records |

---

## License

Proprietary — Radixen. All rights reserved.
