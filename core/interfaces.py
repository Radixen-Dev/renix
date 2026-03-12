"""Abstract base classes for all Renix plugins and I/O modules.

Every concrete implementation of an I/O adapter or plugin must inherit from
the appropriate ABC defined here. Swapping any implementation requires only a
new class and a config change — no graph, node, or existing module changes.

Rules:
- ``core/`` imports nothing from ``modules/``.
- These interfaces are the only cross-boundary contract.
- Never modify this file without an approved GitHub issue.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from langgraph.graph import StateGraph


# ---------------------------------------------------------------------------
# Plugin interfaces
# ---------------------------------------------------------------------------


class SubagentPlugin(ABC):
    """Contract for all LangGraph subagent plugins.

    Each subagent is a self-contained compiled subgraph registered with the
    parent graph via ``AGENTS`` in ``modules/agents/__init__.py``.

    Attributes:
        name: Unique string identifier. Must match the intent labels dispatched
            by the ``route`` node.
        description: Human-readable explanation of when the orchestrator should
            delegate to this agent. Used in the system prompt.
    """

    name: str
    description: str

    @abstractmethod
    def build(self) -> StateGraph:
        """Build and return a compiled subgraph.

        Called once at startup by ``core/graph.py``. The returned subgraph is
        registered as a node in the parent ``StateGraph``.

        Returns:
            A compiled LangGraph ``StateGraph`` ready to be added as a node.

        Raises:
            AgentError: If the subgraph cannot be built due to configuration
                or dependency errors.
        """
        ...


class ToolPlugin(ABC):
    """Contract for all LangChain tool plugins.

    Each tool is converted to a LangChain ``@tool``-decorated callable by
    ``modules/tools/registry.py`` and bound to the ``ToolNode`` inside
    ``tool_use_agent``.

    Attributes:
        name: Unique string identifier for the tool.
        description: Used by LangChain to generate the tool schema for the LLM.
            Should describe what the tool does and when to call it.
    """

    name: str
    description: str

    @abstractmethod
    def run(self, **kwargs: object) -> str:
        """Execute the tool and return a plain-string result.

        Args:
            **kwargs: Tool-specific parameters described in the subclass.

        Returns:
            Plain string result to be returned to the LLM.

        Raises:
            ToolError: If the tool execution fails.
        """
        ...


# ---------------------------------------------------------------------------
# I/O module interfaces
# ---------------------------------------------------------------------------


class WakeWordDetector(ABC):
    """Contract for wake-word detection adapters.

    The ``listen`` node calls this to block until the configured wake word is
    detected before recording begins.
    """

    @abstractmethod
    def start(self) -> None:
        """Initialise and start the wake-word detection engine.

        Raises:
            WakeWordError: If the engine cannot be initialised.
        """
        ...

    @abstractmethod
    def stop(self) -> None:
        """Stop and clean up the wake-word detection engine."""
        ...

    @abstractmethod
    def wait_for_detection(self) -> None:
        """Block the calling thread until the wake word is detected.

        Returns immediately after detection. The caller is responsible for
        triggering the next action (recording).

        Raises:
            WakeWordError: If the detector encounters an unrecoverable error.
        """
        ...


class AudioRecorder(ABC):
    """Contract for microphone capture adapters.

    The ``listen`` node calls ``record()`` immediately after wake-word
    detection. The returned bytes are written directly to ``state["audio_bytes"]``.
    """

    @abstractmethod
    def record(self) -> bytes:
        """Capture audio from the configured input device.

        Returns:
            Raw 16 kHz mono PCM audio as bytes.

        Raises:
            AudioError: If the microphone cannot be accessed or recording fails.
        """
        ...


class Transcriber(ABC):
    """Contract for speech-to-text adapters.

    The ``transcribe`` node passes raw PCM bytes in, receives a transcript
    string out. After calling this, the node must clear ``state["audio_bytes"]``.
    """

    @abstractmethod
    def transcribe(self, audio_data: bytes) -> str:
        """Transcribe raw PCM audio bytes to text.

        Args:
            audio_data: Raw 16 kHz mono PCM audio as bytes.

        Returns:
            Transcribed text string. Empty string if no speech detected.

        Raises:
            TranscriptionError: If the model fails to process the audio.
        """
        ...


class Speaker(ABC):
    """Contract for text-to-speech adapters.

    The ``respond`` node passes the final response string to ``speak()``. This
    is a side-effect-only call; nothing is written back to state.
    """

    @abstractmethod
    def speak(self, text: str) -> None:
        """Convert text to speech and play it through the configured output device.

        Args:
            text: The response string to speak aloud.

        Raises:
            TTSError: If audio output fails.
        """
        ...
