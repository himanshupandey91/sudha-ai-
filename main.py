"""
Sudha AI - Main Cognitive Pipeline

Version 0.4

Current pipeline:

Multimodal Input
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

Important:
- No fake actual outcome is generated.
- Difference is calculated only when a real
  actual outcome is explicitly provided.
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

        This method is only called when an actual
        outcome is explicitly provided.
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
        Run one observation → prediction cycle.

        No actual outcome is generated here.
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

    def run_with_actual(
        self,
        actual,
        text=None,
        voice=None,
        image=None,
        video=None
    ):
        """
        Run a complete prediction → comparison cycle.

        Flow:

        Input
          ↓
        Observation
          ↓
        Prediction
          ↓
        Actual Outcome
          ↓
        Difference

        The actual outcome must be supplied
        explicitly by the caller.
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

        if prediction["status"] != "predicted":
            return prediction

        comparison = self.compare(
            prediction["prediction"],
            actual
        )

        return {
            "status": "completed",
            "observation": observation,
            "prediction": prediction,
            "comparison": comparison
        }
