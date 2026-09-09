from core.perception import PerceptionEngine
from core.perception_observation_provider import (
    PerceptionObservationProvider,
)


def test_text_input_becomes_perception_observation():
    provider = PerceptionObservationProvider(
        lambda: {
            "text": "Hello Sudha"
        }
    )

    result = provider.observe()

    assert result["status"] == "observation_created"
    assert result["modalities"] == ["text"]
    assert result["count"] == 1
    assert result["data"]["text"] == "Hello Sudha"


def test_voice_input_becomes_perception_observation():
    audio = b"voice-data"

    provider = PerceptionObservationProvider(
        lambda: {
            "voice": audio
        }
    )

    result = provider.observe()

    assert result["status"] == "observation_created"
    assert result["modalities"] == ["voice"]
    assert result["count"] == 1
    assert result["data"]["voice"] == audio


def test_image_input_becomes_perception_observation():
    image = b"image-data"

    provider = PerceptionObservationProvider(
        lambda: {
            "image": image
        }
    )

    result = provider.observe()

    assert result["status"] == "observation_created"
    assert result["modalities"] == ["image"]
    assert result["count"] == 1
    assert result["data"]["image"] == image


def test_video_input_becomes_perception_observation():
    video = b"video-data"

    provider = PerceptionObservationProvider(
        lambda: {
            "video": video
        }
    )

    result = provider.observe()

    assert result["status"] == "observation_created"
    assert result["modalities"] == ["video"]
    assert result["count"] == 1
    assert result["data"]["video"] == video


def test_multimodal_input_is_preserved():
    provider = PerceptionObservationProvider(
        lambda: {
            "text": "What is this?",
            "voice": b"voice",
            "image": b"image",
            "video": b"video",
        }
    )

    result = provider.observe()

    assert result["status"] == "observation_created"

    assert result["modalities"] == [
        "text",
        "voice",
        "image",
        "video",
    ]

    assert result["count"] == 4

    assert result["data"]["text"] == "What is this?"
    assert result["data"]["voice"] == b"voice"
    assert result["data"]["image"] == b"image"
    assert result["data"]["video"] == b"video"


def test_provider_uses_supplied_perception_engine():
    perception_engine = PerceptionEngine()

    provider = PerceptionObservationProvider(
        lambda: {
            "text": "Custom engine test"
        },
        perception_engine=perception_engine,
    )

    result = provider.observe()

    assert result["status"] == "observation_created"
    assert result["data"]["text"] == (
        "Custom engine test"
    )


def test_provider_calls_source_once_per_observation():
    calls = []

    def source():
        calls.append("called")

        return {
            "text": "one observation"
        }

    provider = PerceptionObservationProvider(source)

    provider.observe()

    assert calls == ["called"]


def test_provider_calls_source_once_for_each_observation():
    values = [
        "first",
        "second",
    ]

    calls = []

    def source():
        value = values[len(calls)]
        calls.append(value)

        return {
            "text": value
        }

    provider = PerceptionObservationProvider(source)

    first = provider.observe()
    second = provider.observe()

    assert calls == [
        "first",
        "second",
    ]

    assert first["data"]["text"] == "first"
    assert second["data"]["text"] == "second"


def test_provider_does_not_invent_missing_modalities():
    provider = PerceptionObservationProvider(
        lambda: {
            "text": "Only text"
        }
    )

    result = provider.observe()

    assert result["modalities"] == ["text"]
    assert result["count"] == 1

    assert "voice" not in result["data"]
    assert "image" not in result["data"]
    assert "video" not in result["data"]


def test_provider_rejects_non_dictionary_source_output():
    provider = PerceptionObservationProvider(
        lambda: "invalid"
    )

    try:
        provider.observe()
    except TypeError as exc:
        assert str(exc) == (
            "source must return a dictionary"
        )
    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_provider_rejects_unsupported_input():
    provider = PerceptionObservationProvider(
        lambda: {
            "text": "hello",
            "sensor": 123,
        }
    )

    try:
        provider.observe()
    except ValueError as exc:
        assert str(exc) == (
            "unsupported perception inputs: ['sensor']"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_provider_rejects_empty_input():
    provider = PerceptionObservationProvider(
        lambda: {}
    )

    try:
        provider.observe()
    except ValueError as exc:
        assert str(exc) == (
            "source returned no perception inputs"
        )
    else:
        raise AssertionError(
            "Expected ValueError"
        )


def test_provider_requires_callable_source():
    try:
        PerceptionObservationProvider(
            source="not-callable"
        )
    except TypeError as exc:
        assert str(exc) == (
            "source must be callable"
        )
    else:
        raise AssertionError(
            "Expected TypeError"
        )


def test_provider_configuration_is_explicit():
    provider = PerceptionObservationProvider(
        lambda: {
            "text": "configuration"
        }
    )

    configuration = provider.get_configuration()

    assert configuration["provider"] == (
        "PerceptionObservationProvider"
    )

    assert configuration["source_configured"] is True

    assert configuration["perception_engine"] == (
        "PerceptionEngine"
    )

    assert configuration["supported_inputs"] == [
        "image",
        "text",
        "video",
        "voice",
    ]
