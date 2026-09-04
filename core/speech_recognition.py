"""
Sudha AI - Speech Recognition Layer

Version 0.2

Connects the Speech Recognition Layer with
a replaceable Speech Backend.

Flow:

Audio Data
    ↓
Validation
    ↓
Speech Backend
    ↓
Transcribed Text
    ↓
Structured Result

Design goals:
- Replaceable backend architecture
- Explicit validation
- Backend contract enforcement
- Deterministic behavior
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
        Convert audio data into text through
        the configured speech backend.
        """

        validation = self._validate_audio(
            audio_data
        )

        if validation is not None:
            return validation

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

        try:
            text = transcribe(
                bytes(audio_data)
            )

        except Exception as error:
            return {
                "status": "failed",
                "reason": "speech_recognition_backend_error",
                "error": str(error)
            }

        if not isinstance(text, str):
            return {
                "status": "rejected",
                "reason": "speech_recognition_backend_must_return_text"
            }

        return {
            "status": "recognized",
            "text": text
        }

    def _validate_audio(self, audio_data):
        """
        Validate raw audio input.

        Returns:
            Rejection result or None when valid.
        """

        if audio_data is None:
            return {
                "status": "rejected",
                "reason": "audio_data_cannot_be_none"
            }

        if not isinstance(
            audio_data,
            (bytes, bytearray)
        ):
            return {
                "status": "rejected",
                "reason": "audio_data_must_be_bytes"
            }

        if len(audio_data) == 0:
            return {
                "status": "rejected",
                "reason": "audio_data_cannot_be_empty"
            }

        return None
