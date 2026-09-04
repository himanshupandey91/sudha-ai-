"""
Sudha AI - Speech Recognition Layer

Version 0.1

Provides a controlled interface between audio input
and speech-to-text processing.

Version 0.1:
- Validates audio input.
- Provides a speech-to-text interface.
- Does NOT yet connect to a real STT model.

Design goals:
- Clean architecture
- Explicit validation
- Deterministic behavior
- Replaceable STT backend
- No external side effects
- Fully testable
"""


class SpeechRecognitionEngine:

    def __init__(self, backend=None):
        """
        Initialize the Speech Recognition Engine.

        backend:
            Optional speech-to-text backend.

            The backend must provide:
                transcribe(audio_data)
        """

        self.backend = backend

    def recognize(self, audio_data):
        """
        Convert audio data into text.
        """

        if audio_data is None:
            return {
                "status": "rejected",
                "reason": "audio_data_cannot_be_none"
            }

        if not isinstance(audio_data, (bytes, bytearray)):
            return {
                "status": "rejected",
                "reason": "audio_data_must_be_bytes"
            }

        if len(audio_data) == 0:
            return {
                "status": "rejected",
                "reason": "audio_data_cannot_be_empty"
            }

        if self.backend is None:
            return {
                "status": "unavailable",
                "reason": "speech_recognition_backend_not_configured"
            }

        transcribe = getattr(
            self.backend,
            "transcribe",
            None
        )

        if not callable(transcribe):
            return {
                "status": "rejected",
                "reason": "invalid_speech_recognition_backend"
            }

        result = transcribe(
            bytes(audio_data)
        )

        if not isinstance(result, str):
            return {
                "status": "rejected",
                "reason": "speech_recognition_backend_must_return_text"
            }

        return {
            "status": "recognized",
            "text": result
        }
