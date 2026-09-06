"""
Sudha AI - Cognitive Pipeline

Version 0.1

Connects the existing perception and prediction
components into one controlled cognitive cycle.

Flow:

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

Important:
- Does not invent an actual outcome.
- Does not modify memory yet.
- Does not perform autonomous external actions.
- Uses existing Sudha AI components.
"""

from core.perception import PerceptionEngine
from core.prediction import PredictionEngine
from core.difference import DifferenceEngine


class CognitivePipeline:

    def __init__(
        self,
        perception=None,
        prediction=None,
        difference=None
    ):
        """
        Initialize the cognitive pipeline.
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
        Compare prediction against an explicitly
        supplied actual outcome.
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
        Run observation → prediction.

        No actual outcome is invented.
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
        Run the complete cognitive cycle.

        Input
          ↓
        Observation
          ↓
        Prediction
          ↓
        Actual Outcome
          ↓
        Difference
        """

        result = self.run(
            text=text,
            voice=voice,
            image=image,
            video=video
        )

        if result["status"] != "predicted":
            return result

        comparison = self.compare(
            result["prediction"]["prediction"],
            actual
        )

        return {
            "status": "completed",
            "observation": result["observation"],
            "prediction": result["prediction"],
            "comparison": comparison
        }
