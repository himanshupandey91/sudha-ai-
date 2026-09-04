"""
Sudha AI - Whisper Speech Recognition Backend

Version 0.1

Architecture adapter for a future Whisper-based
Speech-to-Text implementation.

This module intentionally does NOT load a Whisper
model yet.

Design goals:
- Keep Whisper integration isolated
- Preserve the SpeechBackend contract
- Validate audio input
- Avoid external side effects
- Make future model integration testable
"""

from core.speech_backend import SpeechBackend


class WhisperSpeechBackend(SpeechBackend):

    def __init__(self, model=None):
        """
        Initialize the Whisper backend.

        model:
            Future Whisper model instance.

            None means that the real Whisper model
            has not been configured yet.
        """

        self.model = model

    def transcribe(self, audio_data):
        """
        Transcribe audio data using the configured
        Whisper model.

        The actual Whisper inference will be added
        in a later step.
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
