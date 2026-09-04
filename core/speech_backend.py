"""
Sudha AI - Speech Recognition Backend

Version 0.3

Provides the backend interface for speech recognition.

Architecture:

Audio Data
    ↓
Speech Backend
    ↓
Text

This version keeps the backend interface clean so that
a real local Speech-to-Text engine can be connected later.

Design goals:
- Replaceable backend architecture
- Explicit validation
- Deterministic testing
- No external side effects
- Clear error handling
"""


class SpeechBackend:

    def transcribe(self, audio_data):
        """
        Transcribe audio data into text.

        Real speech-recognition backends must implement
        this method.
        """

        raise NotImplementedError(
            "Speech backend must implement transcribe()"
        )


class DeterministicSpeechBackend(SpeechBackend):

    def __init__(self, text=""):
        """
        Create a deterministic backend for testing.

        text:
            Text returned for valid audio.
        """

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string"
            )

        self.text = text

    def transcribe(self, audio_data):
        """
        Return predetermined text.

        This backend is used for architecture testing.
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

        return self.text


class UnavailableSpeechBackend(SpeechBackend):

    def transcribe(self, audio_data):
        """
        Placeholder for a real Speech-to-Text backend.

        A real STT engine will replace this backend later.
        """

        raise RuntimeError(
            "real_speech_recognition_backend_not_configured"
        )
