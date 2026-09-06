"""
Sudha AI - Cognitive Pipeline

Version 0.5

Cognitive flow:

Input
  ↓
Perception
  ↓
Unified Observation
  ↓
Prediction
  ↓
Actual Outcome
  ↓
Difference
  ↓
Learning

Compatibility:
- Preserves the original CognitivePipeline API
- Supports multimodal observation
- Keeps prediction / comparison / learning separate
- Does not invent actual outcomes
- Keeps components replaceable and testable
"""

from core.perception import PerceptionEngine
from core.prediction import PredictionEngine
from core.difference import DifferenceEngine
from core.learning import LearningEngine


class CognitivePipeline:

    def __init__(
        self,
        perception=None,
        prediction=None,
        difference=None,
        learning=None
    ):
        self.perception = (
            perception
            if perception is not None
            else PerceptionEngine()
        )

        self.prediction = (
            prediction
            if prediction is not None
            else PredictionEngine()
        )

        self.difference = (
            difference
            if difference is not None
            else DifferenceEngine()
        )

        self.learning = (
            learning
            if learning is not None
            else LearningEngine()
        )

    def observe(
        self,
        text=None,
        voice=None,
        image=None,
        video=None
    ):
        """
        Create a unified multimodal observation.
        """

        try:
            return self.perception.create_multimodal_observation(
                text=text,
                voice=voice,
                image=image,
                video=video
            )

        except Exception as error:
            return {
                "status": "failed",
                "reason": "perception_failed",
                "error": str(error)
            }

    def perceive(self, input_data):
        """
        Compatibility helper for newer perception-style callers.
        """

        if isinstance(input_data, dict):
            return self.observe(
                text=input_data.get("text"),
                voice=input_data.get(
                    "voice",
                    input_data.get("audio")
                ),
                image=input_data.get("image"),
                video=input_data.get("video")
            )

        return self.observe(
            text=input_data
        )

    def perceive_text(self, text):
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

        return self.observe(text=text)

    def perceive_audio(self, audio):
        return self.observe(
            voice=audio
        )

    def perceive_camera(self, frame):
        return self.observe(
            image=frame
        )

    def perceive_video(self, frame):
        return self.observe(
            video=frame
        )

    def predict(self, observation):
        """
        Generate a prediction from an observation.
        """

        if not isinstance(observation, dict):
            return {
                "status": "rejected",
                "reason": "observation_must_be_a_dictionary"
            }

        if observation.get("status") != "observation_created":
            return {
                "status": "rejected",
                "reason": "invalid_observation"
            }

        data = observation.get("data")

        try:
            prediction = self.prediction.predict(
                data
            )

        except Exception as error:
            return {
                "status": "failed",
                "reason": "prediction_failed",
                "error": str(error)
            }

        return {
            "status": "predicted",
            "prediction": prediction
        }

    def compare(
        self,
        prediction,
        actual
    ):
        """
        Compare prediction against an explicitly
        supplied actual outcome.
        """

        try:
            difference = self.difference.calculate(
                prediction,
                actual
            )

        except Exception as error:
            return {
                "status": "failed",
                "reason": "difference_calculation_failed",
                "error": str(error)
            }

        return {
            "status": "compared",
            "prediction": prediction,
            "actual": actual,
            "difference": difference
        }

    def learn(self, difference):
        """
        Convert prediction error into a learning signal.
        """

        try:
            result = self.learning.learn(
                difference
            )

        except Exception as error:
            return {
                "status": "failed",
                "reason": "learning_engine_error",
                "error": str(error)
            }

        return {
            "status": "learned",
            "result": result
        }

    def run(
        self,
        text=None,
        voice=None,
        image=None,
        video=None
    ):
        """
        Run:

        Observation
            ↓
        Prediction

        No actual outcome is invented.
        No learning occurs here.
        """

        observation = self.observe(
            text=text,
            voice=voice,
            image=image,
            video=video
        )

        if observation.get("status") != "observation_created":
            return observation

        prediction = self.predict(
            observation
        )

        if prediction.get("status") != "predicted":
            return prediction

        return {
            "status": "predicted",
            "observation": observation,
            "prediction": prediction
        }

    def run_with_actual(
        self,
        actual,
        text=None,
        voice=None,
        image=None,
        video=None
    ):
        """
        Complete cognitive learning cycle:

        Input
          ↓
        Observation
          ↓
        Prediction
          ↓
        Actual Outcome
          ↓
        Difference
          ↓
        Learning
        """

        observation = self.observe(
            text=text,
            voice=voice,
            image=image,
            video=video
        )

        if observation.get("status") != "observation_created":
            return observation

        prediction = self.predict(
            observation
        )

        if prediction.get("status") != "predicted":
            return prediction

        comparison = self.compare(
            prediction["prediction"],
            actual
        )

        if comparison.get("status") != "compared":
            return comparison

        learning = self.learn(
            comparison["difference"]
        )

        return {
            "status": "completed",
            "observation": observation,
            "prediction": prediction,
            "comparison": comparison,
            "learning": learning
        }

    def get_configuration(self):
        return {
            "perception": type(
                self.perception
            ).__name__,
            "prediction": type(
                self.prediction
            ).__name__,
            "difference": type(
                self.difference
            ).__name__,
            "learning": type(
                self.learning
            ).__name__
        }


# New descriptive alias.
# Existing CognitivePipeline API remains unchanged.
CognitivePerceptionPipeline = CognitivePipeline
