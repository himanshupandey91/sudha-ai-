"""
Tests for Sudha AI Perception Engine.
"""

from core.perception import PerceptionEngine


def create_engine():
    return PerceptionEngine()


def test_text_perception():
    engine = create_engine()

    result = engine.perceive_text("Hello Sudha")

    assert result["status"] == "perceived"
    assert result["modality"] == "text"
    assert result["data"] == "Hello Sudha"


def test_voice_perception():
    engine = create_engine()

    audio_data = b"audio-data"

    result = engine.perceive_voice(audio_data)

    assert result["status"] == "perceived"
    assert result["modality"] == "voice"
    assert result["data"] == audio_data


def test_image_perception():
    engine = create_engine()

    image_data = b"image-data"

    result = engine.perceive_image(image_data)

    assert result["status"] == "perceived"
    assert result["modality"] == "image"
    assert result["data"] == image_data


def test_video_perception():
    engine = create_engine()

    video_data = b"video-data"

    result = engine.perceive_video(video_data)

    assert result["status"] == "perceived"
    assert result["modality"] == "video"
    assert result["data"] == video_data


def test_unsupported_modality_is_rejected():
    engine = create_engine()

    result = engine.perceive(
        "sensor",
        "data"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "modality_not_supported"


def test_non_string_modality_is_rejected():
    engine = create_engine()

    result = engine.perceive(
        123,
        "data"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "modality_must_be_a_string"


def test_none_data_is_rejected():
    engine = create_engine()

    result = engine.perceive(
        "text",
        None
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "data_cannot_be_none"
