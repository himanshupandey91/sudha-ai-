"""
Sudha AI - Camera Capture Foundation

Version 0.1

Provides a controlled abstraction for real camera capture.

Design goals:
- Camera device abstraction
- Explicit configuration
- Safe frame capture
- No automatic camera access during import
- Testable architecture
- No network access
- No AI inference
"""

from core.video import VideoEngine


class CameraEngine:

    def __init__(
        self,
        camera_index=0,
        width=640,
        height=480,
        fps=30
    ):
        """
        Initialize the camera engine.

        The camera is NOT opened during initialization.
        """

        if not isinstance(camera_index, int):
            raise TypeError(
                "camera_index must be an integer"
            )

        if camera_index < 0:
            raise ValueError(
                "camera_index must be zero or greater"
            )

        self.camera_index = camera_index

        self.video_engine = VideoEngine(
            width=width,
            height=height,
            fps=fps
        )

        self._camera = None

    def is_open(self):
        """
        Return whether a camera device is currently open.
        """

        return self._camera is not None

    def attach_camera(self, camera):
        """
        Attach a camera-like object.

        The object must provide:
            read()

        This abstraction allows real camera hardware
        and fake cameras to use the same interface.
        """

        if camera is None:
            raise ValueError(
                "camera cannot be None"
            )

        read = getattr(
            camera,
            "read",
            None
        )

        if not callable(read):
            raise TypeError(
                "camera must provide read()"
            )

        self._camera = camera

    def capture_frame(
        self,
        pixel_format="rgb"
    ):
        """
        Capture one frame from the attached camera.

        Returns a validated Sudha AI video frame.
        """

        if self._camera is None:
            return {
                "status": "unavailable",
                "reason": "camera_not_attached"
            }

        try:
            success, frame = self._camera.read()

        except Exception as error:
            return {
                "status": "failed",
                "reason": "camera_read_failed",
                "error": str(error)
            }

        if not success:
            return {
                "status": "failed",
                "reason": "camera_frame_not_available"
            }

        result = self.video_engine.create_video_frame(
            frame,
            pixel_format=pixel_format
        )

        if result["status"] != "received":
            return result

        result["camera_index"] = self.camera_index

        return result

    def release(self):
        """
        Release the attached camera.
        """

        if self._camera is None:
            return

        release = getattr(
            self._camera,
            "release",
            None
        )

        if callable(release):
            release()

        self._camera = None

    def get_configuration(self):
        """
        Return camera and video configuration.
        """

        configuration = (
            self.video_engine.get_configuration()
        )

        configuration["camera_index"] = (
            self.camera_index
        )

        configuration["camera_open"] = (
            self.is_open()
        )

        return configuration
