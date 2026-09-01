"""
Sudha AI - Prediction Loop

Connects:
Observation → Prediction → Difference → World Model
"""

from core.prediction import PredictionEngine
from core.difference import DifferenceEngine
from core.world_model import WorldModel


class PredictionLoop:

    def __init__(self):
        self.predictor = PredictionEngine()
        self.difference_engine = DifferenceEngine()
        self.world_model = WorldModel()

    def process(self, observation, actual):
        """
        Complete prediction cycle.

        Observation
            ↓
        Prediction
            ↓
        Difference
            ↓
        World Model
        """

        prediction = self.predictor.predict(observation)

        difference = self.difference_engine.calculate(
            prediction,
            actual
        )

        state = self.world_model.update(
            observation=observation,
            prediction=prediction,
            actual=actual,
            difference=difference
        )

        return state
