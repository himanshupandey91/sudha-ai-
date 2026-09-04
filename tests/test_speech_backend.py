"""
Tests for Sudha AI Speech Recognition Backend.
"""

import pytest

from core.speech_backend import (
    SpeechBackend,
    TestSpeechBackend
)


def test_base_backend_requires_transcribe():
    backend = SpeechBackend()

    with pytest.raises(NotImplementedError):
        backend.transcribe(b"audio-data")


def test_test_backend_returns_text():
    backend = TestSpeechBackend(
        text="Hello Sudha"
    )

    result = backend.transcribe(
        b"audio-data"
    )

    assert result == "Hello Sudha"


def test_test_backend_accepts_bytearray():
    backend = TestSpeechBackend(
        text="Hello Sudha"
    )

    result = backend.transcribe(
        bytearray(b"audio-data")
    )

    assert result == "Hello Sudha"


def test_test_backend_rejects_non_bytes():
    backend = TestSpeechBackend(
        text="Hello Sudha"
    )

    with pytest.raises(TypeError):
        backend.transcribe(
            "audio-data"
        )


def test_test_backend_rejects_empty_audio():
    backend = TestSpeechBackend(
        text="Hello Sudha"
    )

    with pytest.raises(ValueError):
        backend.transcribe(
            b""
        )


def test_test_backend_requires_string_text():
    with pytest.raises(TypeError):
        TestSpeechBackend(
            text=123
        )
