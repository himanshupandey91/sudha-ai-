"""
Sudha AI - Cognitive Pipeline

Version 0.3

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
Learning Signal

Important:
- Actual outcome is never invented.
- Learning occurs only when an actual outcome is supplied.
- LearningEngine receives the prediction difference.
- No autonomous external actions.
- Components remain replaceable and testable.
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

    def learn(self, difference):
        """
        Convert prediction error into a
        learning signal.

        The existing LearningEngine accepts
        only the prediction difference.
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
        Run observation → prediction.

        No actual outcome is invented.
        No learning occurs in this method.
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
        Run the complete cognitive learning cycle.

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
        Learning Signal
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
