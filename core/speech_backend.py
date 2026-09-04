"""
Sudha AI - Speech Recognition Backend

Version 0.1

Defines the backend interface used by the
Speech Recognition Layer.

Version 0.1:
- Provides a controlled backend contract.
- Provides a deterministic test backend.
- Does NOT yet load a real speech model.

Design goals:
- Replaceable backend architecture
- Explicit validation
- Deterministic testing
- No external side effects
"""


class SpeechBackend:

    def transcribe(self, audio_data):
        """
        Transcribe audio data.

        Subclasses or real speech-recognition
        backends must implement this method.
        """

        raise NotImplementedError(
            "Speech backend must implement transcribe()"
        )


class TestSpeechBackend(SpeechBackend):

    def __init__(self, text=""):
        """
        Create a deterministic backend for testing.

        text:
            Text that will be returned for valid audio.
        """

        if not isinstance(text, str):
            raise TypeError(
                "text must be a string"
            )

        self.text = text

    def transcribe(self, audio_data):
        """
        Return predetermined text.

        This backend exists only for testing
        the speech-recognition architecture.
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
