"""
Sudha AI - Whisper Speech Recognition Backend

Version 0.2

Architecture adapter for a future local Whisper-based
Speech-to-Text implementation.

Version 0.2:
- Adds explicit model configuration state.
- Supports configurable model path.
- Preserves the SpeechBackend contract.
- Does not download or load external models.
- Keeps inference isolated from the rest of Sudha AI.

Design goals:
- Local/offline architecture
- Replaceable backend
- Explicit configuration
- Deterministic testing
- No automatic downloads
- No external side effects
"""

from core.speech_backend import SpeechBackend


class WhisperSpeechBackend(SpeechBackend):

    def __init__(
        self,
        model=None,
        model_path=None
    ):
        """
        Initialize the Whisper backend.

        model:
            Optional already-loaded Whisper model.

        model_path:
            Optional path identifying the local
            Whisper model configuration.

        The backend does not automatically download
        or load a model.
        """

        if model_path is not None:
            if not isinstance(model_path, str):
                raise TypeError(
                    "model_path must be a string"
                )

            if model_path.strip() == "":
                raise ValueError(
                    "model_path cannot be empty"
                )

        self.model = model
        self.model_path = model_path

    def is_configured(self):
        """
        Return whether a Whisper model is configured.
        """

        return self.model is not None

    def transcribe(self, audio_data):
        """
        Transcribe audio data using the configured
        Whisper model.
        """

        if not isinstance(
            audio_data,
            (bytes, bytearray)
        ):
            raise TypeError(
                "audio_data must be bytes or bytearray"
            )

        if len(audio_data) == 0:
            raise ValueError(
                "audio_data cannot be empty"
            )

        if self.model is None:
            raise RuntimeError(
                "whisper_model_not_configured"
            )

        transcribe = getattr(
            self.model,
            "transcribe",
            None
        )

        if not callable(transcribe):
            raise TypeError(
                "whisper_model_must_provide_transcribe"
            )

        result = transcribe(
            bytes(audio_data)
        )

        if not isinstance(result, str):
            raise TypeError(
                "whisper_model_must_return_text"
            )

        return result
