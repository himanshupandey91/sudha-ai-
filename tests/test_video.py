"""
Sudha AI - Video Input Tests

Version 0.1
"""

from core.video import VideoEngine


def test_video_engine_default_configuration():
    engine = VideoEngine()

    assert engine.get_configuration() == {
        "width": 640,
        "height": 480,
        "fps": 30,
        "supported_formats": [
            "bgr",
            "gray",
            "rgb"
        ]
    }


def test_video_engine_custom_configuration():
    engine = VideoEngine(
        width=1280,
        height=720,
        fps=60
    )

    config = engine.get_configuration()

    assert config["width"] == 1280
    assert config["height"] == 720
    assert config["fps"] == 60


def test_video_engine_accepts_valid_frame():
    engine = VideoEngine()

    result = engine.validate_frame(
        b"fake-video-frame"
    )

    assert result["status"] == "valid"
    assert result["size"] == len(
        b"fake-video-frame"
    )


def test_video_engine_rejects_none_frame():
    engine = VideoEngine()

    result = engine.validate_frame(
        None
    )

    assert result == {
        "status": "rejected",
        "reason": "frame_cannot_be_none"
    }


def test_video_engine_rejects_empty_frame():
    engine = VideoEngine()

    result = engine.validate_frame(
        b""
    )

    assert result == {
        "status": "rejected",
        "reason": "frame_cannot_be_empty"
    }


def test_video_engine_rejects_invalid_frame_type():
    engine = VideoEngine()

    result = engine.validate_frame(
        "not-a-frame"
    )

    assert result == {
        "status": "rejected",
        "reason": "frame_must_be_bytes"
    }


def test_video_engine_creates_rgb_frame():
    engine = VideoEngine()

    result = engine.create_video_frame(
        b"frame-data",
        pixel_format="rgb"
    )

    assert result["status"] == "received"
    assert result["format"] == "rgb"
    assert result["width"] == 640
    assert result["height"] == 480
    assert result["fps"] == 30
    assert result["data"] == b"frame-data"


def test_video_engine_creates_bgr_frame():
    engine = VideoEngine()

    result = engine.create_video_frame(
        b"frame-data",
        pixel_format="bgr"
    )

    assert result["status"] == "received"
    assert result["format"] == "bgr"


def test_video_engine_creates_gray_frame():
    engine = VideoEngine()

    result = engine.create_video_frame(
        b"frame-data",
        pixel_format="gray"
    )

    assert result["status"] == "received"
    assert result["format"] == "gray"


def test_video_engine_rejects_unsupported_format():
    engine = VideoEngine()

    result = engine.create_video_frame(
        b"frame-data",
        pixel_format="xyz"
    )

    assert result == {
        "status": "rejected",
        "reason": "pixel_format_not_supported",
        "pixel_format": "xyz"
    }


def test_video_engine_copies_frame_data():
    engine = VideoEngine()

    original = bytearray(
        b"camera-frame"
    )

    result = engine.create_video_frame(
        original
    )

    assert result["data"] == b"camera-frame"
    assert isinstance(
        result["data"],
        bytes
    )
