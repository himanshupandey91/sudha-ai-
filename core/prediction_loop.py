"""
Sudha AI - Prediction Loop

Connects:
Observation
→ Prediction
→ Difference
→ Attention
→ Learning
→ Curiosity
→ World Model
→ Goal Generation
"""

from core.prediction import PredictionEngine
from core.difference import DifferenceEngine
from core.attention import AttentionEngine
from core.learning import LearningEngine
from core.curiosity import CuriosityEngine
from core.world_model import WorldModel
from core.goal import GoalEngine


class PredictionLoop:

    def __init__(self):
        self.predictor = PredictionEngine()
        self.difference_engine = DifferenceEngine()
        self.attention = AttentionEngine()
        self.learning = LearningEngine()
        self.curiosity = CuriosityEngine()
        self.world_model = WorldModel()
        self.goal = GoalEngine()

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

        curiosity_state = self.curiosity.calculate(difference)

        state = self.world_model.update(
            observation=observation,
            prediction=prediction,
            actual=actual,
            difference=difference
        )

        goal_state = self.goal.generate(state)

        state["attention"] = attention_state
        state["learning"] = learning_state
        state["curiosity"] = curiosity_state
        state["goal"] = goal_state

        return state
