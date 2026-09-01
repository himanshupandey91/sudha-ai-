"""
Sudha AI - Prediction Loop

Connects:
Observation → Prediction → Difference
"""

from core.prediction import PredictionEngine
from core.difference import DifferenceEngine


class PredictionLoop:

    def __init__(self):
        self.predictor = PredictionEngine()
        self.difference_engine = DifferenceEngine()

    def process(self, observation, actual):
        """
        Make a prediction and compare it with reality.
        """

        prediction = self.predictor.predict(observation)

        difference = self.difference_engine.calculate(
            prediction,
            actual
        )

        return {
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": difference
        }
