"""
Sudha AI - Speech Cognitive Bridge

Version 0.1

Connects:

Audio
  ↓
Speech Recognition
  ↓
Recognized Text
  ↓
Cognitive Pipeline
  ↓
Unified Observation

Design goals:
- Connect real speech recognition to perception.
- Keep speech recognition separate from cognition.
- Preserve CognitivePipeline API.
- Never invent transcription.
- Never invent actual outcomes.
- No learning is performed here.
- Deterministic and testable.
- No external side effects.
"""

from core.cognitive_pipeline import CognitivePipeline
from core.speech_recognition import SpeechRecognitionEngine


class SpeechCognitiveBridge:

    def __init__(
        self,
        speech_recognition=None,
        cognitive_pipeline=None
    ):
        self.speech_recognition = (
            speech_recognition
            if speech_recognition is not None
            else SpeechRecognitionEngine()
        )

        self.cognitive_pipeline = (
            cognitive_pipeline
            if cognitive_pipeline is not None
            else CognitivePipeline()
        )

    def recognize(self, audio_data):
        """
        Convert audio into recognized text.
        """

        return self.speech_recognition.recognize(
            audio_data
        )

    def recognize_file(self, audio_file):
        """
        Convert an audio file into recognized text.
        """

        return self.speech_recognition.recognize_file(
            audio_file
        )

    def perceive_audio(self, audio_data):
        """
        Convert raw audio into a cognitive observation.
        """

        recognition = self.recognize(
            audio_data
        )

        if recognition.get("status") != "recognized":
            return recognition

        text = recognition.get("text")

        return self.cognitive_pipeline.observe(
            text=text
        )

    def perceive_file(self, audio_file):
        """
        Convert an audio file into a cognitive observation.
        """

        recognition = self.recognize_file(
            audio_file
        )

        if recognition.get("status") != "recognized":
            return recognition

        text = recognition.get("text")

        return self.cognitive_pipeline.observe(
            text=text
        )

    def run(self, audio_data):
        """
        Run:

        Audio
          ↓
        Speech Recognition
          ↓
        Cognitive Observation

        No prediction.
        No actual outcome.
        No learning.
        """

        observation = self.perceive_audio(
            audio_data
        )

        if observation.get("status") != "observation_created":
            return observation

        return {
            "status": "observed",
            "observation": observation
        }

    def run_file(self, audio_file):
        """
        Run the speech-to-cognition pipeline
        using an audio file.
        """

        observation = self.perceive_file(
            audio_file
        )

        if observation.get("status") != "observation_created":
            return observation

        return {
            "status": "observed",
            "observation": observation
        }

    def get_configuration(self):
        """
        Return bridge configuration.
        """

        return {
            "speech_recognition": type(
                self.speech_recognition
            ).__name__,
            "cognitive_pipeline": type(
                self.cognitive_pipeline
            ).__name__
        }
