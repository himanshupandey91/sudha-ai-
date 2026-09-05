"""
Sudha AI - Multimodal Perception Tests

Version 0.2

Tests unified multimodal observation
creation inside the Perception Layer.
"""

from core.perception import PerceptionEngine


def create_engine():
    return PerceptionEngine()


def test_text_perception():
    engine = create_engine()

    result = engine.perceive_text(
        "hello sudha"
    )

    assert result["status"] == "perceived"
    assert result["modality"] == "text"
    assert result["data"] == "hello sudha"


def test_voice_perception():
    engine = create_engine()

    audio = b"voice-data"

    result = engine.perceive_voice(
        audio
    )

    assert result["status"] == "perceived"
    assert result["modality"] == "voice"
    assert result["data"] == audio


def test_image_perception():
    engine = create_engine()

    image = b"image-data"

    result = engine.perceive_image(
        image
    )

    assert result["status"] == "perceived"
    assert result["modality"] == "image"
    assert result["data"] == image


def test_video_perception():
    engine = create_engine()

    video = b"video-data"

    result = engine.perceive_video(
        video
    )

    assert result["status"] == "perceived"
    assert result["modality"] == "video"
    assert result["data"] == video


def test_create_observation_with_text():
    engine = create_engine()

    text = engine.perceive_text(
        "hello"
    )

    result = engine.create_observation(
        [text]
    )

    assert result["status"] == "observation_created"
    assert result["modalities"] == ["text"]
    assert result["data"]["text"] == "hello"
    assert result["count"] == 1


def test_create_multimodal_observation():
    engine = create_engine()

    result = engine.create_multimodal_observation(
        text="hello",
        voice=b"voice",
        image=b"image",
        video=b"video"
    )

    assert result["status"] == "observation_created"

    assert result["modalities"] == [
        "text",
        "voice",
        "image",
        "video"
    ]

    assert result["data"]["text"] == "hello"
    assert result["data"]["voice"] == b"voice"
    assert result["data"]["image"] == b"image"
    assert result["data"]["video"] == b"video"

    assert result["count"] == 4


def test_multimodal_observation_with_only_text():
    engine = create_engine()

    result = engine.create_multimodal_observation(
        text="only text"
    )

    assert result["status"] == "observation_created"
    assert result["modalities"] == ["text"]
    assert result["data"]["text"] == "only text"
    assert result["count"] == 1


def test_multimodal_observation_with_text_and_voice():
    engine = create_engine()

    result = engine.create_multimodal_observation(
        text="hello",
        voice=b"audio"
    )

    assert result["status"] == "observation_created"

    assert result["modalities"] == [
        "text",
        "voice"
    ]

    assert result["count"] == 2


def test_empty_multimodal_observation_is_rejected():
    engine = create_engine()

    result = engine.create_multimodal_observation()

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "perceptions_cannot_be_empty"
    )


def test_observation_requires_list():
    engine = create_engine()

    result = engine.create_observation(
        "not-a-list"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "perceptions_must_be_a_list"
    )


def test_observation_rejects_empty_list():
    engine = create_engine()

    result = engine.create_observation([])

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "perceptions_cannot_be_empty"
    )


def test_observation_rejects_non_dictionary():
    engine = create_engine()

    result = engine.create_observation(
        ["invalid"]
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "perception_must_be_a_dictionary"
    )


def test_observation_rejects_invalid_perception():
    engine = create_engine()

    result = engine.create_observation(
        [
            {
                "status": "rejected",
                "modality": "text",
                "data": "bad"
            }
        ]
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "invalid_perception"
    )


def test_observation_rejects_missing_data():
    engine = create_engine()

    result = engine.create_observation(
        [
            {
                "status": "perceived",
                "modality": "text"
            }
        ]
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "perception_data_missing"
    )


def test_observation_preserves_multiple_modalities():
    engine = create_engine()

    perceptions = [
        engine.perceive_text("hello"),
        engine.perceive_image(b"image"),
        engine.perceive_video(b"video")
    ]

    result = engine.create_observation(
        perceptions
    )

    assert result["status"] == "observation_created"

    assert result["modalities"] == [
        "text",
        "image",
        "video"
    ]

    assert result["count"] == 3
