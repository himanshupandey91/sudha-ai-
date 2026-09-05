from core.perception import PerceptionEngine


def test_text_perception():
    engine = PerceptionEngine()

    result = engine.perceive_text(
        "Hello Sudha"
    )

    assert result["status"] == "perceived"
    assert result["modality"] == "text"
    assert result["data"] == "Hello Sudha"


def test_voice_perception():
    engine = PerceptionEngine()

    audio = b"voice-data"

    result = engine.perceive_voice(
        audio
    )

    assert result["status"] == "perceived"
    assert result["modality"] == "voice"
    assert result["data"] == audio


def test_image_perception():
    engine = PerceptionEngine()

    image = b"image-data"

    result = engine.perceive_image(
        image
    )

    assert result["status"] == "perceived"
    assert result["modality"] == "image"
    assert result["data"] == image


def test_video_perception():
    engine = PerceptionEngine()

    video = b"video-data"

    result = engine.perceive_video(
        video
    )

    assert result["status"] == "perceived"
    assert result["modality"] == "video"
    assert result["data"] == video


def test_single_observation():
    engine = PerceptionEngine()

    text = engine.perceive_text(
        "Hello"
    )

    result = engine.create_observation(
        [text]
    )

    assert result["status"] == "observation_created"
    assert result["modalities"] == ["text"]
    assert result["count"] == 1
    assert result["data"]["text"] == "Hello"


def test_full_multimodal_observation():
    engine = PerceptionEngine()

    result = engine.create_multimodal_observation(
        text="Hello",
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

    assert result["count"] == 4

    assert result["data"]["text"] == "Hello"
    assert result["data"]["voice"] == b"voice"
    assert result["data"]["image"] == b"image"
    assert result["data"]["video"] == b"video"


def test_text_only_multimodal_observation():
    engine = PerceptionEngine()

    result = engine.create_multimodal_observation(
        text="Hello"
    )

    assert result["status"] == "observation_created"
    assert result["modalities"] == ["text"]
    assert result["count"] == 1


def test_text_and_voice_observation():
    engine = PerceptionEngine()

    result = engine.create_multimodal_observation(
        text="Hello",
        voice=b"voice"
    )

    assert result["status"] == "observation_created"
    assert result["modalities"] == [
        "text",
        "voice"
    ]
    assert result["count"] == 2


def test_empty_multimodal_observation_rejected():
    engine = PerceptionEngine()

    result = engine.create_multimodal_observation()

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "perceptions_cannot_be_empty"
    )


def test_non_list_observation_rejected():
    engine = PerceptionEngine()

    result = engine.create_observation(
        "invalid"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "perceptions_must_be_a_list"
    )


def test_empty_observation_rejected():
    engine = PerceptionEngine()

    result = engine.create_observation(
        []
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "perceptions_cannot_be_empty"
    )


def test_non_dictionary_perception_rejected():
    engine = PerceptionEngine()

    result = engine.create_observation(
        ["invalid"]
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "perception_must_be_a_dictionary"
    )


def test_invalid_perception_rejected():
    engine = PerceptionEngine()

    result = engine.create_observation(
        [{
            "status": "rejected",
            "modality": "text",
            "data": "hello"
        }]
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "invalid_perception"
    )


def test_missing_perception_data_rejected():
    engine = PerceptionEngine()

    result = engine.create_observation(
        [{
            "status": "perceived",
            "modality": "text"
        }]
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "perception_data_missing"
    )


def test_multiple_modalities_are_preserved():
    engine = PerceptionEngine()

    text = engine.perceive_text(
        "What is this?"
    )

    image = engine.perceive_image(
        b"camera-frame"
    )

    result = engine.create_observation(
        [text, image]
    )

    assert result["status"] == "observation_created"
    assert result["modalities"] == [
        "text",
        "image"
    ]

    assert result["data"]["text"] == (
        "What is this?"
    )

    assert result["data"]["image"] == (
        b"camera-frame"
    )
