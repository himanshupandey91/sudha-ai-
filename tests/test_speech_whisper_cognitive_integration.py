"""
Sudha AI - Real Whisper to Cognitive Pipeline Integration

Step 64-A

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
Prediction
    ↓
Actual Outcome
    ↓
Difference
    ↓
Learning

This test intentionally uses:

- real whisper.cpp executable
- real tiny.en model
- real JFK sample audio

No deterministic speech mock is used for the
speech-recognition boundary.

The actual outcome is supplied explicitly to the
cognitive pipeline. It is never invented by the test.
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


def create_real_speech_engine():
    """
    Create the real Whisper speech-recognition engine.

    This helper performs only environment validation and
    dependency construction. It does not mock Whisper.
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

    return SpeechRecognitionEngine(
        backend=backend
    )


def recognize_jfk_audio():
    """
    Run the real JFK audio through whisper.cpp.
    """

    speech = create_real_speech_engine()

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

    return result


def test_real_whisper_recognizes_jfk_audio():
    """
    Verify that real whisper.cpp recognizes the real
    JFK sample audio.
    """

    result = recognize_jfk_audio()

    assert result["status"] == "recognized"

    assert isinstance(
        result["text"],
        str
    )

    assert result["text"].strip()


def test_real_whisper_output_enters_cognitive_perception():
    """
    Verify that the real Whisper transcription crosses
    the speech-recognition boundary and enters perception.
    """

    recognition = recognize_jfk_audio()

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


def test_real_speech_to_perception_preserves_transcription():
    """
    Verify that the exact transcription produced by
    whisper.cpp is preserved by the perception layer.
    """

    recognition = recognize_jfk_audio()

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
    Verify the cognitive pipeline configuration after
    real speech has entered perception.
    """

    recognition = recognize_jfk_audio()

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


def test_real_speech_reaches_prediction():
    """
    Verify that the observation produced from real
    Whisper speech can enter the prediction stage.
    """

    recognition = recognize_jfk_audio()

    pipeline = CognitivePipeline()

    observation = pipeline.perceive_text(
        recognition["text"]
    )

    prediction = pipeline.predict(
        observation
    )

    assert prediction["status"] == (
        "predicted"
    )

    assert "prediction" in prediction


def test_real_speech_reaches_difference_and_learning():
    """
    Verify the complete cognitive path:

    Real speech
        ↓
    Whisper
        ↓
    Perception
        ↓
    Prediction
        ↓
    Explicit actual outcome
        ↓
    Difference
        ↓
    Learning

    The actual outcome is intentionally supplied by
    the test. It is not generated by Whisper or the
    cognitive pipeline.
    """

    recognition = recognize_jfk_audio()

    pipeline = CognitivePipeline()

    actual = {
        "text": recognition["text"]
    }

    result = pipeline.run_with_actual(
        actual=actual,
        text=recognition["text"]
    )

    assert result["status"] == (
        "completed"
    )

    assert (
        result["observation"]["status"]
        == "observation_created"
    )

    assert (
        result["prediction"]["status"]
        == "predicted"
    )

    assert (
        result["comparison"]["status"]
        == "compared"
    )

    assert (
        result["learning"]["status"]
        == "learned"
    )

    assert (
        result["comparison"]["actual"]
        == actual
    )

    assert "difference" in (
        result["comparison"]
    )

    assert "result" in (
        result["learning"]
    )
