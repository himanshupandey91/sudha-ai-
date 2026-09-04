"""
Sudha AI - Audio Perception Integration

Version 0.1

Connects the Audio Engine with the Perception Layer.

Flow:

Audio Input
    ↓
Audio Validation
    ↓
Perception Layer
    ↓
Structured Audio Perception

Design goals:
- Explicit validation
- Clean separation of responsibilities
- Deterministic behavior
- No external side effects
- Fully testable
"""

from core.audio import AudioEngine
from core.perception import PerceptionEngine


class AudioPerceptionEngine:

    def __init__(self, audio_engine=None, perception_engine=None):
        """
        Initialize the Audio Perception Engine.

        Existing engines can be supplied for testing
        or controlled integration.
        """

        self.audio = (
            audio_engine
            if audio_engine is not None
            else AudioEngine()
        )

        self.perception = (
            perception_engine
            if perception_engine is not None
            else PerceptionEngine()
        )

    def process(self, audio_data, audio_format="wav"):
        """
        Validate audio and pass it to the Perception Layer.
        """

        validation = self.audio.validate(audio_data)

        if validation["status"] != "valid":
            return validation

        audio_input = self.audio.create_audio_input(
            audio_data,
            audio_format
        )

        if audio_input["status"] != "received":
            return audio_input

        perception = self.perception.perceive_voice(
            audio_input["data"]
        )

        if perception["status"] != "perceived":
            return perception

        return {
            "status": "processed",
            "modality": perception["modality"],
            "format": audio_input["format"],
            "sample_rate": audio_input["sample_rate"],
            "channels": audio_input["channels"],
            "size": audio_input["size"],
            "data": perception["data"]
        }
