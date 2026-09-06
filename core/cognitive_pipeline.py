"""
Sudha AI - Cognitive Perception Pipeline

Version 0.4

Connects:

Input
  ↓
Perception
  ↓
Observation
  ↓
Cognitive Processing

Supported inputs:
- Text
- Audio
- Generic perception objects

Design goals:
- Convert external input into a normalized observation
- Preserve the original input
- Keep perception separate from reasoning
- Support future camera/video integration
- Deterministic and testable
- No external side effects
"""

from core.perception import PerceptionEngine


class CognitivePerceptionPipeline:

    def __init__(self, perception=None):
        self.perception = (
            perception
            if perception is not None
            else PerceptionEngine()
        )

        self.last_observation = None
        self.history = []

    def perceive(self, input_data):
        """
        Convert input into an observation.
        """

        try:
            result = self.perception.process(
                input_data
            )

        except Exception as error:
            return {
                "status": "failed",
                "reason": "perception_failed",
                "error": str(error)
            }

        if not isinstance(result, dict):
            result = {
                "observation": result
            }

        observation = dict(result)

        self.last_observation = observation
        self.history.append(observation)

        return {
            "status": "perceived",
            "observation": observation
        }

    def perceive_text(self, text):
        """
        Process text input.
        """

        if not isinstance(text, str):
            return {
                "status": "rejected",
                "reason": "invalid_text"
            }

        if not text.strip():
            return {
                "status": "rejected",
                "reason": "empty_text"
            }

        return self.perceive({
            "type": "text",
            "text": text
        })

    def perceive_audio(self, audio):
        """
        Process audio input.

        The audio object is passed to the perception
        engine without inventing a transcription.
        """

        return self.perceive({
            "type": "audio",
            "audio": audio
        })

    def perceive_camera(self, frame):
        """
        Process a camera frame.
        """

        return self.perceive({
            "type": "camera",
            "frame": frame
        })

    def perceive_video(self, frame):
        """
        Process a video frame.
        """

        return self.perceive({
            "type": "video",
            "frame": frame
        })

    def get_last_observation(self):
        """
        Return the latest observation.
        """

        if self.last_observation is None:
            return None

        return dict(
            self.last_observation
        )

    def get_history(self):
        """
        Return perception history.
        """

        return [
            dict(item)
            for item in self.history
        ]

    def clear_history(self):
        """
        Clear stored perception history.
        """

        self.history.clear()
        self.last_observation = None

        return {
            "status": "cleared"
        }

    def get_history_size(self):
        """
        Return number of stored observations.
        """

        return len(self.history)

    def get_configuration(self):
        """
        Return pipeline configuration.
        """

        return {
            "perception_engine": type(
                self.perception
            ).__name__,
            "history_size": len(
                self.history
            ),
            "has_last_observation": (
                self.last_observation is not None
            )
        }
