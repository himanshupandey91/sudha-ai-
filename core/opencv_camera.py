"""
Sudha AI - OpenCV Camera Adapter

Version 0.1

Connects Sudha AI's CameraEngine architecture
to a real camera through OpenCV.

Design goals:
- Real camera hardware support
- Explicit camera opening
- Safe frame reading
- Explicit release
- No camera access during import
- No network access
- Testable adapter architecture
"""


class OpenCVCameraAdapter:

    def __init__(
        self,
        camera_index=0,
        cv2_module=None
    ):
        """
        Initialize the OpenCV camera adapter.

        The camera is NOT opened automatically.

        camera_index:
            Operating-system camera index.

        cv2_module:
            Optional OpenCV module injection.
            This allows testing without installing
            or accessing real OpenCV hardware.
        """

        if not isinstance(
            camera_index,
            int
        ):
            raise TypeError(
                "camera_index must be an integer"
            )

        if camera_index < 0:
            raise ValueError(
                "camera_index must be zero or greater"
            )

        self.camera_index = camera_index
        self.cv2 = cv2_module
        self._capture = None

    def _load_cv2(self):
        """
        Load OpenCV only when the adapter is used.
        """

        if self.cv2 is not None:
            return self.cv2

        try:
            import cv2

        except ImportError as error:

            raise RuntimeError(
                "opencv_not_installed"
            ) from error

        self.cv2 = cv2

        return self.cv2

    def open(self):
        """
        Open the configured camera.
        """

        if self._capture is not None:
            return True

        cv2 = self._load_cv2()

        try:
            capture = cv2.VideoCapture(
                self.camera_index
            )

        except Exception as error:

            raise RuntimeError(
                "camera_open_failed"
            ) from error

        if capture is None:
            raise RuntimeError(
                "camera_open_failed"
            )

        is_opened = getattr(
            capture,
            "isOpened",
            None
        )

        if not callable(is_opened):

            try:
                capture.release()
            except Exception:
                pass

            raise RuntimeError(
                "camera_invalid_capture_object"
            )

        try:
            opened = is_opened()

        except Exception as error:

            try:
                capture.release()
            except Exception:
                pass

            raise RuntimeError(
                "camera_open_status_failed"
            ) from error

        if not opened:

            try:
                capture.release()
            except Exception:
                pass

            raise RuntimeError(
                "camera_not_available"
            )

        self._capture = capture

        return True

    def read(self):
        """
        Read one frame from the real camera.

        Returns:
            (success, frame)
        """

        if self._capture is None:
            raise RuntimeError(
                "camera_not_open"
            )

        try:
            success, frame = (
                self._capture.read()
            )

        except Exception as error:

            raise RuntimeError(
                "camera_read_failed"
            ) from error

        return success, frame

    def release(self):
        """
        Release the camera device.
        """

        if self._capture is None:
            return

        release = getattr(
            self._capture,
            "release",
            None
        )

        if callable(release):
            release()

        self._capture = None

    def is_open(self):
        """
        Return whether the adapter currently
        has an open camera.
        """

        return self._capture is not None

    def get_configuration(self):
        """
        Return adapter configuration.
        """

        return {
            "camera_index": self.camera_index,
            "camera_open": self.is_open()
        }
