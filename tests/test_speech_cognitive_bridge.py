from pathlib import Path

from core.speech_backend import SpeechBackend
from core.speech_recognition import SpeechRecognitionEngine
from core.cognitive_pipeline import CognitivePipeline
from core.speech_cognitive_bridge import SpeechCognitiveBridge


class DeterministicSpeechBackend(SpeechBackend):
    def __init__(self, text="hello from speech"):
        self.text = text
        self.audio_calls = 0
        self.file_calls = 0

    def transcribe(self, audio_data):
        self.audio_calls += 1
        return self.text

    def transcribe_file(self, audio_file):
        self.file_calls += 1
        return self.text


class SpyCognitivePipeline:
    def __init__(self):
        self.observe_calls = []

    def observe(self, text=None, voice=None, image=None, video=None):
        self.observe_calls.append(
            {
                "text": text,
                "voice": voice,
                "image": image,
                "video": video,
            }
        )

        return {
            "status": "observation_created",
            "data": {
                "text": text,
                "voice": voice,
                "image": image,
                "video": video,
            },
        }


class FailingSpeechBackend(SpeechBackend):
    def transcribe(self, audio_data):
        raise RuntimeError("transcription_failed")

    def transcribe_file(self, audio_file):
        raise RuntimeError("file_transcription_failed")


def create_bridge(
    speech_backend=None,
    cognitive_pipeline=None,
):
    if speech_backend is None:
        speech_backend = DeterministicSpeechBackend()

    speech_recognition = SpeechRecognitionEngine(
        backend=speech_backend
    )

    if cognitive_pipeline is None:
        cognitive_pipeline = SpyCognitivePipeline()

    return SpeechCognitiveBridge(
        speech_recognition=speech_recognition,
        cognitive_pipeline=cognitive_pipeline,
    )


def test_bridge_can_be_created():
    bridge = create_bridge()

    assert isinstance(bridge, SpeechCognitiveBridge)


def test_bridge_configuration_is_correct():
    bridge = create_bridge()

    configuration = bridge.get_configuration()

    assert configuration["speech_recognition"] == (
        "SpeechRecognitionEngine"
    )
    assert configuration["cognitive_pipeline"] == (
        "SpyCognitivePipeline"
    )


def test_recognize_returns_speech_recognition_result():
    backend = DeterministicSpeechBackend(
        text="real recognized text"
    )

    bridge = create_bridge(
        speech_backend=backend
    )

    result = bridge.recognize(b"audio")

    assert result["status"] == "recognized"
    assert result["text"] == "real recognized text"
    assert backend.audio_calls == 1


def test_perceive_audio_connects_recognized_text_to_cognitive_pipeline():
    backend = DeterministicSpeechBackend(
        text="hello Sudha"
    )

    pipeline = SpyCognitivePipeline()

    bridge = create_bridge(
        speech_backend=backend,
        cognitive_pipeline=pipeline,
    )

    result = bridge.perceive_audio(b"audio")

    assert result["status"] == "observation_created"

    assert len(pipeline.observe_calls) == 1

    call = pipeline.observe_calls[0]

    assert call["text"] == "hello Sudha"
    assert call["voice"] is None
    assert call["image"] is None
    assert call["video"] is None


def test_perceive_file_connects_recognized_text_to_cognitive_pipeline(
    tmp_path: Path,
):
    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"dummy wav data")

    backend = DeterministicSpeechBackend(
        text="hello from file"
    )

    pipeline = SpyCognitivePipeline()

    bridge = create_bridge(
        speech_backend=backend,
        cognitive_pipeline=pipeline,
    )

    result = bridge.perceive_file(audio_file)

    assert result["status"] == "observation_created"

    assert backend.file_calls == 1

    assert len(pipeline.observe_calls) == 1

    call = pipeline.observe_calls[0]

    assert call["text"] == "hello from file"


def test_run_returns_observed_result():
    backend = DeterministicSpeechBackend(
        text="run test"
    )

    bridge = create_bridge(
        speech_backend=backend
    )

    result = bridge.run(b"audio")

    assert result["status"] == "observed"
    assert result["observation"]["status"] == (
        "observation_created"
    )


def test_run_file_returns_observed_result(tmp_path: Path):
    audio_file = tmp_path / "sample.wav"
    audio_file.write_bytes(b"dummy wav data")

    backend = DeterministicSpeechBackend(
        text="file run test"
    )

    bridge = create_bridge(
        speech_backend=backend
    )

    result = bridge.run_file(audio_file)

    assert result["status"] == "observed"
    assert result["observation"]["status"] == (
        "observation_created"
    )


def test_recognition_failure_is_propagated():
    backend = FailingSpeechBackend()

    bridge = create_bridge(
        speech_backend=backend
    )

    result = bridge.perceive_audio(b"audio")

    assert result["status"] == "failed"
    assert result["reason"] == (
        "speech_recognition_backend_error"
    )


def test_recognition_failure_does_not_call_cognitive_pipeline():
    backend = FailingSpeechBackend()
    pipeline = SpyCognitivePipeline()

    bridge = create_bridge(
        speech_backend=backend,
        cognitive_pipeline=pipeline,
    )

    result = bridge.perceive_audio(b"audio")

    assert result["status"] == "failed"
    assert len(pipeline.observe_calls) == 0


def test_invalid_audio_is_rejected_before_speech_backend():
    backend = DeterministicSpeechBackend()

    bridge = create_bridge(
        speech_backend=backend
    )

    result = bridge.perceive_audio(b"")

    assert result["status"] == "rejected"
    assert result["reason"] == "audio_data_cannot_be_empty"
    assert backend.audio_calls == 0


def test_missing_audio_file_is_rejected(tmp_path: Path):
    missing_file = tmp_path / "missing.wav"

    backend = DeterministicSpeechBackend()

    bridge = create_bridge(
        speech_backend=backend
    )

    result = bridge.perceive_file(missing_file)

    assert result["status"] == "rejected"
    assert result["reason"] == "audio_file_not_found"
    assert backend.file_calls == 0


def test_bridge_does_not_perform_prediction_or_learning():
    backend = DeterministicSpeechBackend(
        text="observation only"
    )

    pipeline = SpyCognitivePipeline()

    bridge = create_bridge(
        speech_backend=backend,
        cognitive_pipeline=pipeline,
    )

    result = bridge.run(b"audio")

    assert result["status"] == "observed"

    assert len(pipeline.observe_calls) == 1

    observation = result["observation"]

    assert observation["status"] == "observation_created"
    assert observation["data"]["text"] == (
        "observation only"
    )

    assert "prediction" not in result
    assert "learning" not in result
    assert "difference" not in result
