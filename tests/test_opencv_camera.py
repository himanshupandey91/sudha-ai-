"""
Sudha AI - OpenCV Camera Adapter Tests

Version 0.1

Tests the OpenCVCameraAdapter without requiring
real camera hardware or OpenCV installation.
"""

import pytest

from core.opencv_camera import (
    OpenCVCameraAdapter
)


class FakeCapture:

    def __init__(
        self,
        opened=True,
        success=True,
        frame=b"fake-frame"
    ):
        self.opened = opened
        self.success = success
        self.frame = frame
        self.read_count = 0
        self.release_count = 0

    def isOpened(self):
        return self.opened

    def read(self):
        self.read_count += 1

        return (
            self.success,
            self.frame
        )

    def release(self):
        self.release_count += 1


class FakeCV2:

    def __init__(
        self,
        capture
    ):
        self.capture = capture
        self.requested_index = None

    def VideoCapture(
        self,
        camera_index
    ):
        self.requested_index = camera_index

        return self.capture


def test_opencv_camera_default_configuration():

    adapter = OpenCVCameraAdapter()

    assert adapter.get_configuration() == {
        "camera_index": 0,
        "camera_open": False
    }


def test_opencv_camera_custom_index():

    adapter = OpenCVCameraAdapter(
        camera_index=2
    )

    assert adapter.camera_index == 2

    assert adapter.get_configuration() == {
        "camera_index": 2,
        "camera_open": False
    }


def test_opencv_camera_rejects_invalid_index():

    with pytest.raises(
        TypeError,
        match="camera_index must be an integer"
    ):
        OpenCVCameraAdapter(
            camera_index="0"
        )


def test_opencv_camera_rejects_negative_index():

    with pytest.raises(
        ValueError,
        match="camera_index must be zero or greater"
    ):
        OpenCVCameraAdapter(
            camera_index=-1
        )


def test_opencv_camera_does_not_open_during_initialization():

    capture = FakeCapture()

    fake_cv2 = FakeCV2(
        capture
    )

    adapter = OpenCVCameraAdapter(
        cv2_module=fake_cv2
    )

    assert adapter.is_open() is False
    assert fake_cv2.requested_index is None


def test_opencv_camera_opens_successfully():

    capture = FakeCapture()

    fake_cv2 = FakeCV2(
        capture
    )

    adapter = OpenCVCameraAdapter(
        camera_index=1,
        cv2_module=fake_cv2
    )

    result = adapter.open()

    assert result is True
    assert adapter.is_open() is True
    assert fake_cv2.requested_index == 1


def test_opencv_camera_read_requires_open_camera():

    adapter = OpenCVCameraAdapter(
        cv2_module=FakeCV2(
            FakeCapture()
        )
    )

    with pytest.raises(
        RuntimeError,
        match="camera_not_open"
    ):
        adapter.read()


def test_opencv_camera_reads_frame():

    capture = FakeCapture(
        frame=b"real-camera-frame"
    )

    fake_cv2 = FakeCV2(
        capture
    )

    adapter = OpenCVCameraAdapter(
        cv2_module=fake_cv2
    )

    adapter.open()

    success, frame = adapter.read()

    assert success is True
    assert frame == b"real-camera-frame"
    assert capture.read_count == 1


def test_opencv_camera_handles_failed_frame():

    capture = FakeCapture(
        success=False
    )

    fake_cv2 = FakeCV2(
        capture
    )

    adapter = OpenCVCameraAdapter(
        cv2_module=fake_cv2
    )

    adapter.open()

    success, frame = adapter.read()

    assert success is False
    assert frame == b"fake-frame"


def test_opencv_camera_rejects_unavailable_camera():

    capture = FakeCapture(
        opened=False
    )

    fake_cv2 = FakeCV2(
        capture
    )

    adapter = OpenCVCameraAdapter(
        cv2_module=fake_cv2
    )

    with pytest.raises(
        RuntimeError,
        match="camera_not_available"
    ):
        adapter.open()

    assert adapter.is_open() is False
    assert capture.release_count == 1


def test_opencv_camera_release():

    capture = FakeCapture()

    fake_cv2 = FakeCV2(
        capture
    )

    adapter = OpenCVCameraAdapter(
        cv2_module=fake_cv2
    )

    adapter.open()

    assert adapter.is_open() is True

    adapter.release()

    assert adapter.is_open() is False
    assert capture.release_count == 1


def test_opencv_camera_release_without_open_camera():

    adapter = OpenCVCameraAdapter(
        cv2_module=FakeCV2(
            FakeCapture()
        )
    )

    adapter.release()

    assert adapter.is_open() is False


def test_opencv_camera_open_is_idempotent():

    capture = FakeCapture()

    fake_cv2 = FakeCV2(
        capture
    )

    adapter = OpenCVCameraAdapter(
        cv2_module=fake_cv2
    )

    assert adapter.open() is True
    assert adapter.open() is True

    assert adapter.is_open() is True
    assert fake_cv2.requested_index == 0


def test_opencv_camera_handles_missing_opencv():

    adapter = OpenCVCameraAdapter()

    adapter.cv2 = None

    with pytest.raises(
        RuntimeError,
        match="opencv_not_installed"
    ):
        adapter._load_cv2()


def test_opencv_camera_invalid_capture_object():

    class InvalidCV2:

        def VideoCapture(
            self,
            camera_index
        ):
            return object()

    adapter = OpenCVCameraAdapter(
        cv2_module=InvalidCV2()
    )

    with pytest.raises(
        RuntimeError,
        match="camera_invalid_capture_object"
    ):
        adapter.open()
