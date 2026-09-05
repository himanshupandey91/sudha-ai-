"""
Sudha AI - Camera Capture Tests

Version 0.1

Tests the CameraEngine using a fake camera.

No physical camera hardware is required.
"""

from core.camera import CameraEngine


class FakeCamera:

    def __init__(
        self,
        frame=b"fake-camera-frame",
        success=True
    ):
        self.frame = frame
        self.success = success
        self.read_count = 0
        self.released = False

    def read(self):
        self.read_count += 1

        return (
            self.success,
            self.frame
        )

    def release(self):
        self.released = True


def test_camera_engine_default_configuration():

    camera = CameraEngine()

    assert camera.get_configuration() == {
        "width": 640,
        "height": 480,
        "fps": 30,
        "supported_formats": [
            "bgr",
            "gray",
            "rgb"
        ],
        "camera_index": 0,
        "camera_open": False
    }


def test_camera_engine_custom_configuration():

    camera = CameraEngine(
        camera_index=2,
        width=1280,
        height=720,
        fps=60
    )

    configuration = (
        camera.get_configuration()
    )

    assert configuration["camera_index"] == 2
    assert configuration["width"] == 1280
    assert configuration["height"] == 720
    assert configuration["fps"] == 60
    assert configuration["camera_open"] is False


def test_camera_engine_rejects_invalid_camera_index():

    try:
        CameraEngine(
            camera_index="0"
        )
        assert False
    except TypeError as error:
        assert str(error) == (
            "camera_index must be an integer"
        )


def test_camera_engine_rejects_negative_camera_index():

    try:
        CameraEngine(
            camera_index=-1
        )
        assert False
    except ValueError as error:
        assert str(error) == (
            "camera_index must be zero or greater"
        )


def test_camera_engine_starts_without_opening_camera():

    camera = CameraEngine()

    assert camera.is_open() is False


def test_camera_engine_rejects_missing_camera():

    camera = CameraEngine()

    result = camera.capture_frame()

    assert result == {
        "status": "unavailable",
        "reason": "camera_not_attached"
    }


def test_camera_engine_attaches_fake_camera():

    camera = CameraEngine()

    fake_camera = FakeCamera()

    camera.attach_camera(
        fake_camera
    )

    assert camera.is_open() is True


def test_camera_engine_rejects_none_camera():

    camera = CameraEngine()

    try:
        camera.attach_camera(None)
        assert False
    except ValueError as error:
        assert str(error) == (
            "camera cannot be None"
        )


def test_camera_engine_rejects_invalid_camera():

    camera = CameraEngine()

    try:
        camera.attach_camera(
            object()
        )
        assert False
    except TypeError as error:
        assert str(error) == (
            "camera must provide read()"
        )


def test_camera_engine_captures_frame():

    camera = CameraEngine()

    fake_camera = FakeCamera(
        frame=b"camera-frame"
    )

    camera.attach_camera(
        fake_camera
    )

    result = camera.capture_frame()

    assert result["status"] == "received"
    assert result["format"] == "rgb"
    assert result["camera_index"] == 0
    assert result["data"] == (
        b"camera-frame"
    )

    assert fake_camera.read_count == 1


def test_camera_engine_captures_bgr_frame():

    camera = CameraEngine()

    fake_camera = FakeCamera()

    camera.attach_camera(
        fake_camera
    )

    result = camera.capture_frame(
        pixel_format="bgr"
    )

    assert result["status"] == "received"
    assert result["format"] == "bgr"


def test_camera_engine_handles_failed_capture():

    camera = CameraEngine()

    fake_camera = FakeCamera(
        success=False
    )

    camera.attach_camera(
        fake_camera
    )

    result = camera.capture_frame()

    assert result == {
        "status": "failed",
        "reason": "camera_frame_not_available"
    }


def test_camera_engine_handles_camera_exception():

    camera = CameraEngine()

    class FailingCamera:

        def read(self):
            raise RuntimeError(
                "camera_failure"
            )

    camera.attach_camera(
        FailingCamera()
    )

    result = camera.capture_frame()

    assert result == {
        "status": "failed",
        "reason": "camera_read_failed",
        "error": "camera_failure"
    }


def test_camera_engine_rejects_unsupported_pixel_format():

    camera = CameraEngine()

    fake_camera = FakeCamera()

    camera.attach_camera(
        fake_camera
    )

    result = camera.capture_frame(
        pixel_format="xyz"
    )

    assert result == {
        "status": "rejected",
        "reason": "pixel_format_not_supported",
        "pixel_format": "xyz"
    }


def test_camera_engine_release():

    camera = CameraEngine()

    fake_camera = FakeCamera()

    camera.attach_camera(
        fake_camera
    )

    assert camera.is_open() is True

    camera.release()

    assert fake_camera.released is True
    assert camera.is_open() is False


def test_camera_engine_release_without_camera():

    camera = CameraEngine()

    camera.release()

    assert camera.is_open() is False
