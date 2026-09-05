"""
Sudha AI - Video Input Foundation

Version 0.1

Provides a controlled foundation for video input.

Design goals:
- Camera/video-frame abstraction
- Frame validation
- Metadata handling
- No external side effects
- No network access
- Fully testable
"""


class VideoEngine:

    SUPPORTED_FORMATS = {
        "rgb",
        "bgr",
        "gray"
    }

    def __init__(
        self,
        width=640,
        height=480,
        fps=30
    ):
        """
        Initialize the video engine.
        """

        if not isinstance(width, int):
            raise TypeError(
                "width must be an integer"
            )

        if width <= 0:
            raise ValueError(
                "width must be greater than zero"
            )

        if not isinstance(height, int):
            raise TypeError(
                "height must be an integer"
            )

        if height <= 0:
            raise ValueError(
                "height must be greater than zero"
            )

        if not isinstance(fps, (int, float)):
            raise TypeError(
                "fps must be a number"
            )

        if fps <= 0:
            raise ValueError(
                "fps must be greater than zero"
            )

        self.width = width
        self.height = height
        self.fps = fps

    def validate_frame(self, frame):
        """
        Validate an incoming video frame.
        """

        if frame is None:
            return {
                "status": "rejected",
                "reason": "frame_cannot_be_none"
            }

        if not isinstance(
            frame,
            (bytes, bytearray)
        ):
            return {
                "status": "rejected",
                "reason": "frame_must_be_bytes"
            }

        if len(frame) == 0:
            return {
                "status": "rejected",
                "reason": "frame_cannot_be_empty"
            }

        return {
            "status": "valid",
            "size": len(frame),
            "width": self.width,
            "height": self.height,
            "fps": self.fps
        }

    def create_video_frame(
        self,
        frame,
        pixel_format="rgb"
    ):
        """
        Convert validated frame data into
        Sudha AI's common internal representation.
        """

        validation = self.validate_frame(
            frame
        )

        if validation["status"] != "valid":
            return validation

        if pixel_format not in self.SUPPORTED_FORMATS:
            return {
                "status": "rejected",
                "reason": "pixel_format_not_supported",
                "pixel_format": pixel_format
            }

        return {
            "status": "received",
            "format": pixel_format,
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "size": len(frame),
            "data": bytes(frame)
        }

    def get_configuration(self):
        """
        Return the current video configuration.
        """

        return {
            "width": self.width,
            "height": self.height,
            "fps": self.fps,
            "supported_formats": sorted(
                self.SUPPORTED_FORMATS
            )
        }
