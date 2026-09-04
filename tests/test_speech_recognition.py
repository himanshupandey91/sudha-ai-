"""
Tests for Sudha AI Speech Recognition Layer.
"""

from core.speech_backend import (
    DeterministicSpeechBackend
)

from core.speech_recognition import (
    SpeechRecognitionEngine
)


def test_recognition_with_backend():
    backend = DeterministicSpeechBackend(
        text="Hello Sudha"
    )

    engine = SpeechRecognitionEngine(
        backend=backend
    )

    result = engine.recognize(
        b"audio-data"
    )

    assert result["status"] == "recognized"
    assert result["text"] == "Hello Sudha"


def test_recognition_accepts_bytearray():
    backend = DeterministicSpeechBackend(
        text="Hello Sudha"
    )

    engine = SpeechRecognitionEngine(
        backend=backend
    )

    result = engine.recognize(
        bytearray(b"audio-data")
    )

    assert result["status"] == "recognized"
    assert result["text"] == "Hello Sudha"


def test_recognition_without_backend():
    engine = SpeechRecognitionEngine()

    result = engine.recognize(
        b"audio-data"
    )

    assert result["status"] == "unavailable"
    assert result["reason"] == (
        "speech_recognition_backend_not_configured"
    )


def test_none_audio_is_rejected():
    backend = DeterministicSpeechBackend(
        text="Hello Sudha"
    )

    engine = SpeechRecognitionEngine(
        backend=backend
    )

    result = engine.recognize(
        None
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "audio_data_cannot_be_none"
    )


def test_non_bytes_audio_is_rejected():
    backend = DeterministicSpeechBackend(
        text="Hello Sudha"
    )

    engine = SpeechRecognitionEngine(
        backend=backend
    )

    result = engine.recognize(
        "audio-data"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "audio_data_must_be_bytes"
    )


def test_empty_audio_is_rejected():
    backend = DeterministicSpeechBackend(
        text="Hello Sudha"
    )

    engine = SpeechRecognitionEngine(
        backend=backend
    )

    result = engine.recognize(
        b""
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "audio_data_cannot_be_empty"
    )


class BadBackend:

    def transcribe(self, audio_data):
        return 123


def test_backend_must_return_text():
    backend = BadBackend()

    engine = SpeechRecognitionEngine(
        backend=backend
    )

    result = engine.recognize(
        b"audio-data"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "speech_recognition_backend_must_return_text"
    )


class FailingBackend:

    def transcribe(self, audio_data):
        raise RuntimeError(
            "backend failure"
        )


def test_backend_errors_are_controlled():
    backend = FailingBackend()

    engine = SpeechRecognitionEngine(
        backend=backend
    )

    result = engine.recognize(
        b"audio-data"
    )

    assert result["status"] == "failed"
    assert result["reason"] == (
        "speech_recognition_backend_error"
    )
    assert result["error"] == "backend failure"
