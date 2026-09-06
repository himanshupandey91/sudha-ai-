"""
Sudha AI - Experience Learning Engine

Version 0.1

Connects:

Prediction
    ↓
Actual Outcome
    ↓
Difference
    ↓
Learning Signal
    ↓
Memory
    ↓
Adaptive Prediction

Design goals:
- Connect existing cognitive components
- Store real experiences
- Never invent actual outcomes
- Use previous experience for future prediction
- Deterministic behavior
- No external side effects
- Fully testable
"""

from core.difference import DifferenceEngine
from core.learning import LearningEngine
from core.adaptive_prediction import AdaptivePredictionEngine
from core.memory import MemoryEngine


class ExperienceLearningEngine:

    def __init__(
        self,
        adaptive_prediction=None,
        difference=None,
        learning=None,
        memory=None
    ):
        """
        Initialize the experience-learning system.
        """

        self.memory = (
            memory
            if memory is not None
            else MemoryEngine()
        )

        self.adaptive_prediction = (
            adaptive_prediction
            if adaptive_prediction is not None
            else AdaptivePredictionEngine(
                memory_engine=self.memory
            )
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

    def predict(self, observation):
        """
        Generate a prediction using previous experience.
        """

        prediction = self.adaptive_prediction.predict(
            observation
        )

        return {
            "status": "predicted",
            "observation": observation,
            "prediction": prediction
        }

    def learn(
        self,
        observation,
        prediction,
        actual
    ):
        """
        Learn from an explicitly supplied actual outcome.

        The actual outcome is never generated internally.
        """

        difference = self.difference.calculate(
            prediction,
            actual
        )

        learning_result = self.learning.learn(
            difference
        )

        memory_result = self.adaptive_prediction.remember(
            observation=observation,
            prediction=prediction,
            actual=actual,
            difference=difference,
            learning=learning_result
        )

        return {
            "status": "learned",
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": difference,
            "learning": learning_result,
            "memory": memory_result
        }

    def run(
        self,
        observation,
        actual=None
    ):
        """
        Run one complete experience-learning cycle.

        Without actual:
            observation → prediction

        With actual:
            observation → prediction → difference
            → learning → memory
        """

        prediction_result = self.predict(
            observation
        )

        if prediction_result["status"] != "predicted":
            return prediction_result

        prediction = prediction_result[
            "prediction"
        ]

        if actual is None:
            return {
                "status": "predicted",
                "observation": observation,
                "prediction": prediction
            }

        learning_result = self.learn(
            observation=observation,
            prediction=prediction,
            actual=actual
        )

        return {
            "status": "completed",
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": learning_result[
                "difference"
            ],
            "learning": learning_result[
                "learning"
            ],
            "memory": learning_result[
                "memory"
            ]
        }

    def get_memory(self):
        """
        Return stored experiences.
        """

        return self.memory.retrieve()

    def get_memory_size(self):
        """
        Return the number of stored experiences.
        """

        return self.memory.size()

    def clear_memory(self):
        """
        Clear all stored experiences.
        """

        return self.memory.clear()
