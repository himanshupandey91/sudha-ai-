"""
Sudha AI - Speech + Whisper Integration Tests

Version 0.1

Tests the integration between:

SpeechRecognitionEngine
        ↓
WhisperCLIBackend
        ↓
whisper-cli

No real Whisper model is required.
"""

from pathlib import Path

from core.speech_recognition import (
    SpeechRecognitionEngine
)

from core.whisper_cli_backend import (
    WhisperCLIBackend
)


class FakeWhisperCLIBackend:

    def __init__(self, text="hello from whisper"):
        self.text = text
        self.received_file = None

    def transcribe_file(self, audio_file):
        self.received_file = audio_file
        return self.text


def create_audio_file(tmp_path):
    audio_file = tmp_path / "test.wav"

    audio_file.write_bytes(
        b"RIFF-fake-wav-data"
    )

    return audio_file


def test_speech_engine_supports_file_backend(
    tmp_path
):
    audio_file = create_audio_file(
        tmp_path
    )

    backend = FakeWhisperCLIBackend(
        text="hello sudha"
    )

    engine = SpeechRecognitionEngine(
        backend=backend
    )

    result = engine.recognize_file(
        audio_file
    )

    assert result == {
        "status": "recognized",
        "text": "hello sudha"
    }

    assert backend.received_file == str(
        audio_file
    )


def test_speech_engine_rejects_backend_without_file_support(
    tmp_path
):
    audio_file = create_audio_file(
        tmp_path
    )

    backend = object()

    engine = SpeechRecognitionEngine(
        backend=backend
    )

    result = engine.recognize_file(
        audio_file
    )

    assert result == {
        "status": "rejected",
        "reason": (
            "speech_recognition_backend_does_not_support_files"
        )
    }


def test_whisper_cli_backend_exposes_file_api(
    tmp_path
):
    executable = tmp_path / "whisper-cli"
    model = tmp_path / "model.bin"
    audio = create_audio_file(
        tmp_path
    )

    executable.write_text(
        "fake executable",
        encoding="utf-8"
    )

    model.write_bytes(
        b"fake-model"
    )

    backend = WhisperCLIBackend(
        executable_path=str(executable),
        model_path=str(model)
    )

    assert callable(
        backend.transcribe_file
    )

    assert backend.is_configured() is True


def test_speech_engine_rejects_missing_audio_file(
    tmp_path
):
    backend = FakeWhisperCLIBackend()

    engine = SpeechRecognitionEngine(
        backend=backend
    )

    result = engine.recognize_file(
        tmp_path / "missing.wav"
    )

    assert result == {
        "status": "rejected",
        "reason": "audio_file_not_found"
    }


def test_speech_engine_handles_file_backend_error(
    tmp_path
):
    audio_file = create_audio_file(
        tmp_path
    )

    class FailingBackend:

        def transcribe_file(self, audio_file):
            raise RuntimeError(
                "whisper_failure"
            )

    engine = SpeechRecognitionEngine(
        backend=FailingBackend()
    )

    result = engine.recognize_file(
        audio_file
    )

    assert result["status"] == "failed"

    assert result["reason"] == (
        "speech_recognition_file_backend_error"
    )

    assert result["error"] == (
        "whisper_failure"
    )
