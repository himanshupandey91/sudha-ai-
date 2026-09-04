"""
Sudha AI - Whisper Speech Recognition Backend Tests

Version 0.1

Tests the isolated Whisper backend adapter
without loading a real Whisper model.
"""

import pytest

from core.whisper_backend import WhisperSpeechBackend


class FakeWhisperModel:

    def __init__(self, result=""):
        self.result = result
        self.received_audio = None

    def transcribe(self, audio_data):
        self.received_audio = audio_data
        return self.result


class FakeModelWithoutTranscribe:
    pass


def test_whisper_backend_accepts_bytes():
    model = FakeWhisperModel("hello")

    backend = WhisperSpeechBackend(
        model=model
    )

    result = backend.transcribe(
        b"audio-data"
    )

    assert result == "hello"


def test_whisper_backend_accepts_bytearray():
    model = FakeWhisperModel("hello")

    backend = WhisperSpeechBackend(
        model=model
    )

    result = backend.transcribe(
        bytearray(b"audio-data")
    )

    assert result == "hello"


def test_whisper_backend_converts_audio_to_bytes():
    model = FakeWhisperModel("hello")

    backend = WhisperSpeechBackend(
        model=model
    )

    audio = bytearray(b"audio-data")

    backend.transcribe(audio)

    assert model.received_audio == b"audio-data"
    assert isinstance(
        model.received_audio,
        bytes
    )


def test_whisper_backend_rejects_invalid_audio():
    model = FakeWhisperModel("hello")

    backend = WhisperSpeechBackend(
        model=model
    )

    with pytest.raises(TypeError):
        backend.transcribe("audio-data")


def test_whisper_backend_rejects_empty_audio():
    model = FakeWhisperModel("hello")

    backend = WhisperSpeechBackend(
        model=model
    )

    with pytest.raises(ValueError):
        backend.transcribe(b"")


def test_whisper_backend_requires_model():
    backend = WhisperSpeechBackend()

    with pytest.raises(RuntimeError):
        backend.transcribe(b"audio-data")


def test_whisper_backend_requires_transcribe_method():
    model = FakeModelWithoutTranscribe()

    backend = WhisperSpeechBackend(
        model=model
    )

    with pytest.raises(TypeError):
        backend.transcribe(b"audio-data")


def test_whisper_backend_requires_text_result():
    model = FakeWhisperModel(
        result=123
    )

    backend = WhisperSpeechBackend(
        model=model
    )

    with pytest.raises(TypeError):
        backend.transcribe(b"audio-data")
