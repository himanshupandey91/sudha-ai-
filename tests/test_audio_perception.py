"""
Tests for Sudha AI Audio Perception Integration.
"""

from core.audio_perception import AudioPerceptionEngine


def create_engine():
    return AudioPerceptionEngine()


def test_audio_perception_processes_valid_wav_audio():
    engine = create_engine()

    audio_data = b"audio-data"

    result = engine.process(
        audio_data,
        "wav"
    )

    assert result["status"] == "processed"
    assert result["modality"] == "voice"
    assert result["format"] == "wav"
    assert result["sample_rate"] == 16000
    assert result["channels"] == 1
    assert result["size"] == len(audio_data)
    assert result["data"] == audio_data


def test_audio_perception_processes_pcm_audio():
    engine = create_engine()

    audio_data = b"pcm-data"

    result = engine.process(
        audio_data,
        "pcm"
    )

    assert result["status"] == "processed"
    assert result["modality"] == "voice"
    assert result["format"] == "pcm"


def test_audio_perception_processes_raw_audio():
    engine = create_engine()

    audio_data = b"raw-data"

    result = engine.process(
        audio_data,
        "raw"
    )

    assert result["status"] == "processed"
    assert result["modality"] == "voice"
    assert result["format"] == "raw"


def test_none_audio_is_rejected():
    engine = create_engine()

    result = engine.process(
        None,
        "wav"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "audio_data_cannot_be_none"


def test_non_bytes_audio_is_rejected():
    engine = create_engine()

    result = engine.process(
        "audio-data",
        "wav"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "audio_data_must_be_bytes"


def test_empty_audio_is_rejected():
    engine = create_engine()

    result = engine.process(
        b"",
        "wav"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "audio_data_cannot_be_empty"


def test_unsupported_audio_format_is_rejected():
    engine = create_engine()

    result = engine.process(
        b"audio-data",
        "mp3"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "audio_format_not_supported"


def test_bytearray_audio_is_supported():
    engine = create_engine()

    audio_data = bytearray(
        b"audio-data"
    )

    result = engine.process(
        audio_data,
        "pcm"
    )

    assert result["status"] == "processed"
    assert result["data"] == bytes(audio_data)
