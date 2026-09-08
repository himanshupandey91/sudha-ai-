"""
Sudha AI - Speech to Cognitive Perception Integration Tests

Step 63-A

Validates the real integration boundary:

Audio bytes
    ↓
SpeechRecognitionEngine
    ↓
Transcribed text
    ↓
CognitivePipeline
    ↓
PerceptionEngine
    ↓
Unified observation

The test uses a deterministic speech backend to isolate the
integration contract. It does not fake the cognitive pipeline;
the speech backend is only the controlled dependency at the
speech-recognition boundary.

The real Whisper.cpp integration remains covered by the existing
Whisper CLI integration tests.
"""

from core.cognitive_pipeline import CognitivePipeline
from core.speech_recognition import SpeechRecognitionEngine


class DeterministicSpeechBackend:
    """
    Controlled speech-recognition dependency for integration testing.

    The backend represents the output boundary of a real speech
    recognizer such as Whisper.cpp.
    """

    def __init__(self, text):
        if not isinstance(text, str):
            raise TypeError("text must be a string")

        if not text.strip():
            raise ValueError("text cannot be empty")

        self.text = text
        self.calls = 0

    def transcribe(self, audio_data):
        if not isinstance(audio_data, (bytes, bytearray)):
            raise TypeError("audio_data must be bytes or bytearray")

        if len(audio_data) == 0:
            raise ValueError("audio_data cannot be empty")

        self.calls += 1
        return self.text


def test_speech_recognition_produces_text():
    backend = DeterministicSpeechBackend(
        "Sudha AI should learn from experience."
    )

    speech = SpeechRecognitionEngine(
        backend=backend
    )

    result = speech.recognize(
        b"deterministic-audio"
    )

    assert result["status"] == "recognized"
    assert result["text"] == (
        "Sudha AI should learn from experience."
    )
    assert backend.calls == 1


def test_recognized_speech_can_enter_cognitive_perception():
    backend = DeterministicSpeechBackend(
        "The system observed a new event."
    )

    speech = SpeechRecognitionEngine(
        backend=backend
    )

    recognition = speech.recognize(
        b"deterministic-audio"
    )

    assert recognition["status"] == "recognized"

    pipeline = CognitivePipeline()

    observation = pipeline.perceive_text(
        recognition["text"]
    )

    assert observation["status"] == "observation_created"

    assert observation["data"]["text"] == (
        "The system observed a new event."
    )


def test_speech_to_perception_preserves_recognized_text():
    expected_text = (
        "Prediction error should update future learning."
    )

    backend = DeterministicSpeechBackend(
        expected_text
    )

    speech = SpeechRecognitionEngine(
        backend=backend
    )

    recognition = speech.recognize(
        b"deterministic-audio"
    )

    pipeline = CognitivePipeline()

    observation = pipeline.perceive_text(
        recognition["text"]
    )

    assert recognition["text"] == expected_text
    assert observation["data"]["text"] == expected_text


def test_invalid_speech_does_not_enter_perception():
    backend = DeterministicSpeechBackend(
        "This text should never be produced."
    )

    speech = SpeechRecognitionEngine(
        backend=backend
    )

    result = speech.recognize(
        b""
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "audio_data_cannot_be_empty"

    pipeline = CognitivePipeline()

    observation = pipeline.perceive_text(
        result.get("text")
    )

    assert observation["status"] == "rejected"
    assert observation["reason"] == "invalid_text"

    assert backend.calls == 0
