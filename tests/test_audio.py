"""
Tests for Sudha AI Audio Engine.
"""

import pytest

from core.audio import AudioEngine


def create_engine():
    return AudioEngine()


def test_audio_engine_default_configuration():
    engine = create_engine()

    configuration = engine.get_configuration()

    assert configuration["sample_rate"] == 16000
    assert configuration["channels"] == 1
    assert configuration["supported_formats"] == [
        "pcm",
        "raw",
        "wav"
    ]


def test_valid_audio_is_accepted():
    engine = create_engine()

    audio_data = b"audio-data"

    result = engine.validate(audio_data)

    assert result["status"] == "valid"
    assert result["size"] == len(audio_data)
    assert result["sample_rate"] == 16000
    assert result["channels"] == 1


def test_none_audio_is_rejected():
    engine = create_engine()

    result = engine.validate(None)

    assert result["status"] == "rejected"
    assert result["reason"] == "audio_data_cannot_be_none"


def test_non_bytes_audio_is_rejected():
    engine = create_engine()

    result = engine.validate("audio-data")

    assert result["status"] == "rejected"
    assert result["reason"] == "audio_data_must_be_bytes"


def test_empty_audio_is_rejected():
    engine = create_engine()

    result = engine.validate(b"")

    assert result["status"] == "rejected"
    assert result["reason"] == "audio_data_cannot_be_empty"


def test_audio_input_is_created():
    engine = create_engine()

    audio_data = b"audio-data"

    result = engine.create_audio_input(
        audio_data,
        "wav"
    )

    assert result["status"] == "received"
    assert result["format"] == "wav"
    assert result["sample_rate"] == 16000
    assert result["channels"] == 1
    assert result["size"] == len(audio_data)
    assert result["data"] == audio_data


def test_unsupported_audio_format_is_rejected():
    engine = create_engine()

    result = engine.create_audio_input(
        b"audio-data",
        "mp3"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "audio_format_not_supported"


def test_bytearray_audio_is_supported():
    engine = create_engine()

    audio_data = bytearray(b"audio-data")

    result = engine.create_audio_input(
        audio_data,
        "pcm"
    )

    assert result["status"] == "received"
    assert result["format"] == "pcm"
    assert result["data"] == bytes(audio_data)


def test_custom_audio_configuration():
    engine = AudioEngine(
        sample_rate=48000,
        channels=2
    )

    configuration = engine.get_configuration()

    assert configuration["sample_rate"] == 48000
    assert configuration["channels"] == 2


def test_invalid_sample_rate_is_rejected():
    with pytest.raises(ValueError):
        AudioEngine(sample_rate=0)


def test_invalid_channels_are_rejected():
    with pytest.raises(ValueError):
        AudioEngine(channels=0)
