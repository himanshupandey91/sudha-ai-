"""
Sudha AI - Experience Learning Engine

Version 0.2

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
World Model
    ↓
Adaptive Prediction

Version 0.2:
- Integrates WorldModel
- Stores completed experiences
- Updates world state after learning
- Preserves previous API behavior
- Never invents actual outcomes
- Deterministic behavior
- No external side effects
"""

from core.difference import DifferenceEngine
from core.learning import LearningEngine
from core.adaptive_prediction import AdaptivePredictionEngine
from core.memory import MemoryEngine
from core.world_model import WorldModel


class ExperienceLearningEngine:

    def __init__(
        self,
        adaptive_prediction=None,
        difference=None,
        learning=None,
        memory=None,
        world_model=None
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

        self.world_model = (
            world_model
            if world_model is not None
            else WorldModel()
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

        world_model_result = (
            self.world_model.update(
                observation=observation,
                prediction=prediction,
                actual=actual,
                difference=difference,
                learning=learning_result
            )
        )

        return {
            "status": "learned",
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": difference,
            "learning": learning_result,
            "memory": memory_result,
            "world_model": world_model_result
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

            observation
                ↓
            prediction
                ↓
            difference
                ↓
            learning
                ↓
            memory
                ↓
            world model
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
            ],
            "world_model": learning_result[
                "world_model"
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

    def get_world_state(self):
        """
        Return the current World Model state.
        """

        return self.world_model.get_state()

    def get_world_history(self):
        """
        Return World Model history.
        """

        return self.world_model.get_history()

    def get_experience_count(self):
        """
        Return the number of experiences
        recorded by the World Model.
        """

        return self.world_model.get_experience_count()

    def clear_memory(self):
        """
        Clear stored experiences and reset
        the World Model.
        """

        memory_result = self.memory.clear()
        world_result = self.world_model.clear()

        return {
            "status": "cleared",
            "memory": memory_result,
            "world_model": world_result
        }
