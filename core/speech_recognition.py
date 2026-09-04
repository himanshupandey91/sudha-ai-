"""
Sudha AI - Speech Recognition Layer

Version 0.3

Connects the Speech Recognition Layer with
replaceable speech backends.

Supports:

1. Raw audio data
2. Local audio files

Architecture:

Raw Audio
    ↓
Validation
    ↓
Speech Backend
    ↓
Transcribed Text

OR

Audio File
    ↓
Validation
    ↓
File-capable Speech Backend
    ↓
Transcribed Text

Design goals:
- Replaceable backend architecture
- Explicit validation
- Backend contract enforcement
- File-based local inference support
- Deterministic behavior
- No automatic downloads
- No external side effects
- Fully testable
"""

from pathlib import Path


class SpeechRecognitionEngine:

    def __init__(self, backend=None):
        """
        Initialize the Speech Recognition Engine.

        backend:
            Optional speech-to-text backend.

            The backend must provide:

                transcribe(audio_data)

            for raw audio.

            A file-capable backend may additionally provide:

                transcribe_file(audio_file)
        """

        self.backend = backend

    def recognize(self, audio_data):
        """
        Convert raw audio data into text through
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
                "reason": (
                    "speech_recognition_backend_not_configured"
                )
            }

        transcribe = getattr(
            self.backend,
            "transcribe",
            None
        )

        if not callable(transcribe):
            return {
                "status": "rejected",
                "reason": (
                    "invalid_speech_recognition_backend"
                )
            }

        try:

            text = transcribe(
                bytes(audio_data)
            )

        except Exception as error:

            return {
                "status": "failed",
                "reason": (
                    "speech_recognition_backend_error"
                ),
                "error": str(error)
            }

        return self._build_result(
            text
        )

    def recognize_file(self, audio_file):
        """
        Convert a local audio file into text.

        The configured backend must provide:

            transcribe_file(audio_file)
        """

        validation = self._validate_audio_file(
            audio_file
        )

        if validation is not None:
            return validation

        if self.backend is None:
            return {
                "status": "unavailable",
                "reason": (
                    "speech_recognition_backend_not_configured"
                )
            }

        transcribe_file = getattr(
            self.backend,
            "transcribe_file",
            None
        )

        if not callable(transcribe_file):
            return {
                "status": "rejected",
                "reason": (
                    "speech_recognition_backend_does_not_support_files"
                )
            }

        try:

            text = transcribe_file(
                str(audio_file)
            )

        except Exception as error:

            return {
                "status": "failed",
                "reason": (
                    "speech_recognition_file_backend_error"
                ),
                "error": str(error)
            }

        return self._build_result(
            text
        )

    def _build_result(self, text):
        """
        Validate backend output and create
        the common recognition result.
        """

        if not isinstance(
            text,
            str
        ):
            return {
                "status": "rejected",
                "reason": (
                    "speech_recognition_backend_must_return_text"
                )
            }

        return {
            "status": "recognized",
            "text": text
        }

    def _validate_audio(self, audio_data):
        """
        Validate raw audio input.
        """

        if audio_data is None:
            return {
                "status": "rejected",
                "reason": (
                    "audio_data_cannot_be_none"
                )
            }

        if not isinstance(
            audio_data,
            (bytes, bytearray)
        ):
            return {
                "status": "rejected",
                "reason": (
                    "audio_data_must_be_bytes"
                )
            }

        if len(audio_data) == 0:
            return {
                "status": "rejected",
                "reason": (
                    "audio_data_cannot_be_empty"
                )
            }

        return None

    def _validate_audio_file(self, audio_file):
        """
        Validate a local audio file path.
        """

        if audio_file is None:
            return {
                "status": "rejected",
                "reason": (
                    "audio_file_cannot_be_none"
                )
            }

        if not isinstance(
            audio_file,
            (str, Path)
        ):
            return {
                "status": "rejected",
                "reason": (
                    "audio_file_must_be_a_path"
                )
            }

        path = Path(
            audio_file
        )

        if str(path).strip() == "":
            return {
                "status": "rejected",
                "reason": (
                    "audio_file_cannot_be_empty"
                )
            }

        if not path.is_file():
            return {
                "status": "rejected",
                "reason": (
                    "audio_file_not_found"
                )
            }

        return None
