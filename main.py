"""
Sudha AI - Main Cognitive Pipeline

Version 0.5

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
  ↓
Learning
  ↓
Memory

Important:
- No fake actual outcome is generated.
- Learning occurs only after an actual outcome is provided.
- Every completed learning cycle is stored in memory.
- Existing run() behavior is preserved.
"""

from core.perception import PerceptionEngine
from core.prediction import PredictionEngine
from core.difference import DifferenceEngine
from core.learning import LearningEngine
from core.memory import MemoryEngine


class SudhaAI:

    def __init__(
        self,
        perception=None,
        prediction=None,
        difference=None,
        learning=None,
        memory=None
    ):
        """
        Initialize the cognitive components.
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

        self.memory = (
            memory
            if memory is not None
            else MemoryEngine()
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
        Compare prediction with actual outcome.
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

    def learn(
        self,
        difference
    ):
        """
        Convert prediction error into
        a learning signal.
        """

        learning = self.learning.learn(
            difference
        )

        return {
            "status": "learned",
            "learning": learning
        }

    def store_experience(
        self,
        observation,
        prediction,
        actual,
        comparison,
        learning
    ):
        """
        Store one complete experience in memory.
        """

        experience = {
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": comparison["difference"],
            "learning_signal": learning["learning_signal"]
        }

        memory_result = self.memory.store(
            experience
        )

        return {
            "status": "memory_updated",
            "memory": memory_result,
            "experience": experience
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
        Run a complete learning cycle.

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
          ↓
        Learning
          ↓
        Memory
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

        memory = self.store_experience(
            observation=observation,
            prediction=prediction["prediction"],
            actual=actual,
            comparison=comparison,
            learning=learning["learning"]
        )

        return {
            "status": "completed",
            "observation": observation,
            "prediction": prediction,
            "comparison": comparison,
            "learning": learning,
            "memory": memory
        }

    def get_memories(self):
        """
        Return all stored experiences.
        """

        return self.memory.retrieve_all()

    def get_recent_memories(
        self,
        count=1
    ):
        """
        Return recent experiences.
        """

        return self.memory.retrieve_recent(
            count
          )
