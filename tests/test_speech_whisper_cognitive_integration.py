"""
Sudha AI - Real Whisper to Cognitive Pipeline Integration

Step 63-B

Validates the real runtime path:

Audio file
    ↓
Whisper.cpp CLI
    ↓
WhisperCLIBackend
    ↓
SpeechRecognitionEngine
    ↓
CognitivePipeline
    ↓
Perception
    ↓
Unified Observation

This test intentionally uses the real whisper.cpp executable,
real tiny.en model, and real JFK sample audio.

No deterministic speech mock is used here.
"""

from pathlib import Path

from core.cognitive_pipeline import CognitivePipeline
from core.speech_recognition import SpeechRecognitionEngine
from core.whisper_cli_backend import WhisperCLIBackend


ROOT = Path(__file__).resolve().parents[1]

WHISPER_EXECUTABLE = (
    ROOT
    / "whisper.cpp"
    / "build"
    / "bin"
    / "whisper-cli"
)

WHISPER_MODEL = (
    ROOT
    / "whisper.cpp"
    / "models"
    / "ggml-tiny.en.bin"
)

JFK_AUDIO = (
    ROOT
    / "whisper.cpp"
    / "samples"
    / "jfk.wav"
)


def test_real_whisper_recognizes_jfk_audio():
    """
    Verify that the real whisper.cpp backend can transcribe
    the real JFK sample audio.
    """

    assert WHISPER_EXECUTABLE.is_file()
    assert WHISPER_MODEL.is_file()
    assert JFK_AUDIO.is_file()

    backend = WhisperCLIBackend(
        executable_path=WHISPER_EXECUTABLE,
        model_path=WHISPER_MODEL,
        timeout_seconds=120,
    )

    assert backend.is_configured()

    speech = SpeechRecognitionEngine(
        backend=backend
    )

    result = speech.recognize_file(
        JFK_AUDIO
    )

    assert result["status"] == "recognized"

    text = result["text"]

    assert isinstance(text, str)
    assert text.strip()

    assert (
        "fellow Americans" in text
    )

    assert (
        "what your country can do for you" in text
    )


def test_real_whisper_output_enters_cognitive_perception():
    """
    Verify the real Whisper transcription can cross the
    speech-recognition boundary and enter CognitivePipeline.
    """

    assert WHISPER_EXECUTABLE.is_file()
    assert WHISPER_MODEL.is_file()
    assert JFK_AUDIO.is_file()

    backend = WhisperCLIBackend(
        executable_path=WHISPER_EXECUTABLE,
        model_path=WHISPER_MODEL,
        timeout_seconds=120,
    )

    speech = SpeechRecognitionEngine(
        backend=backend
    )

    recognition = speech.recognize_file(
        JFK_AUDIO
    )

    assert recognition["status"] == "recognized"

    recognized_text = recognition["text"]

    pipeline = CognitivePipeline()

    observation = pipeline.perceive_text(
        recognized_text
    )

    assert observation["status"] == (
        "observation_created"
    )

    assert (
        observation["data"]["text"]
        == recognized_text
    )


def test_real_speech_to_perception_preserves_transcription():
    """
    Verify that the exact transcription produced by
    whisper.cpp is preserved when entering perception.
    """

    backend = WhisperCLIBackend(
        executable_path=WHISPER_EXECUTABLE,
        model_path=WHISPER_MODEL,
        timeout_seconds=120,
    )

    speech = SpeechRecognitionEngine(
        backend=backend
    )

    recognition = speech.recognize_file(
        JFK_AUDIO
    )

    assert recognition["status"] == "recognized"

    pipeline = CognitivePipeline()

    observation = pipeline.perceive_text(
        recognition["text"]
    )

    assert observation["status"] == (
        "observation_created"
    )

    assert (
        observation["data"]["text"]
        == recognition["text"]
    )


def test_real_speech_pipeline_configuration():
    """
    Verify the cognitive pipeline still exposes its
    expected component configuration after real speech
    has entered perception.
    """

    backend = WhisperCLIBackend(
        executable_path=WHISPER_EXECUTABLE,
        model_path=WHISPER_MODEL,
        timeout_seconds=120,
    )

    speech = SpeechRecognitionEngine(
        backend=backend
    )

    recognition = speech.recognize_file(
        JFK_AUDIO
    )

    assert recognition["status"] == "recognized"

    pipeline = CognitivePipeline()

    observation = pipeline.perceive_text(
        recognition["text"]
    )

    assert observation["status"] == (
        "observation_created"
    )

    configuration = (
        pipeline.get_configuration()
    )

    assert configuration["perception"] == (
        "PerceptionEngine"
    )

    assert configuration["prediction"] == (
        "PredictionEngine"
    )

    assert configuration["difference"] == (
        "DifferenceEngine"
    )

    assert configuration["learning"] == (
        "LearningEngine"
    )
