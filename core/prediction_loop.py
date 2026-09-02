"""
Sudha AI - Prediction Loop

Connects:
Observation → Prediction → Difference → Attention → World Model
"""

from core.prediction import PredictionEngine
from core.difference import DifferenceEngine
from core.attention import AttentionEngine
from core.world_model import WorldModel


class PredictionLoop:

    def __init__(self):
        self.predictor = PredictionEngine()
        self.difference_engine = DifferenceEngine()
        self.attention = AttentionEngine()
        self.world_model = WorldModel()

    def process(self, observation, actual):
        """
        Complete prediction cycle.
        """

        prediction = self.predictor.predict(observation)

        difference = self.difference_engine.calculate(
            prediction,
            actual
        )

        attention_state = self.attention.focus({
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": difference
        })

        state = self.world_model.update(
            observation=observation,
            prediction=prediction,
            actual=actual,
            difference=difference
        )

        state["attention"] = attention_state

        return state
