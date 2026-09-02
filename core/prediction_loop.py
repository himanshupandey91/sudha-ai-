"""
Sudha AI - Prediction Loop

Connects:
Observation → Prediction → Difference → Attention → Learning → World Model
"""

from core.prediction import PredictionEngine
from core.difference import DifferenceEngine
from core.attention import AttentionEngine
from core.learning import LearningEngine
from core.world_model import WorldModel


class PredictionLoop:

    def __init__(self):
        self.predictor = PredictionEngine()
        self.difference_engine = DifferenceEngine()
        self.attention = AttentionEngine()
        self.learning = LearningEngine()
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

        learning_state = self.learning.learn(difference)

        state = self.world_model.update(
            observation=observation,
            prediction=prediction,
            actual=actual,
            difference=difference
        )

        state["attention"] = attention_state
        state["learning"] = learning_state

        return state
