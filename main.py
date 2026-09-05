"""
Sudha AI - Main Cognitive Pipeline

Version 0.3

Current pipeline:

Input
  ↓
Perception
  ↓
Unified Observation
  ↓
Prediction

Difference calculation is kept separate because
it requires both:
    prediction
    actual outcome

No fake actual outcome is generated.
"""

from core.perception import PerceptionEngine
from core.prediction import PredictionEngine
from core.difference import DifferenceEngine


class SudhaAI:

    def __init__(
        self,
        perception=None,
        prediction=None,
        difference=None
    ):
        """
        Initialize the core cognitive components.
        """

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

        return self.perception.create_multimodal_observation(
            text=text,
            voice=voice,
            image=image,
            video=video
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

        prediction = self.prediction.predict(
            data
        )

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
        Compare a prediction with the actual outcome.

        This is the point where real prediction
        error can be measured.
        """

        difference = self.difference.calculate(
            prediction,
            actual
        )

        return {
            "status": "compared",
            "prediction": prediction,
            "actual": actual,
            "difference": difference
        }

    def run(
        self,
        text=None,
        voice=None,
        image=None,
        video=None
    ):
        """
        Run one complete observation → prediction cycle.
        """

        observation = self.observe(
            text=text,
            voice=voice,
            image=image,
            video=video
        )

        if observation["status"] != "observation_created":
            return observation

        prediction = self.predict(
            observation
        )

        return {
            "status": "completed",
            "observation": observation,
            "prediction": prediction
        }
