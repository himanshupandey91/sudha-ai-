"""
Sudha AI - Adaptive Prediction Engine

Version 0.3

Uses previous experiences from MemoryEngine
to improve future predictions.

Architecture:

Current Observation
        ↓
Base Prediction
        ↓
Past Experiences
        ↓
Relevant Experience Selection
        ↓
Adaptive Prediction

Design goals:
- Backward compatibility
- Deterministic behavior
- Experience-based adaptation
- No external side effects
- Replaceable prediction engine
- Replaceable memory engine
- Fully testable

Important:
This module does NOT claim to be AGI.
It provides an explicit experience-based
prediction mechanism.
"""


class AdaptivePredictionEngine:

    def __init__(
        self,
        prediction_engine=None,
        memory_engine=None
    ):
        """
        Initialize the adaptive prediction engine.

        prediction_engine:
            Object providing:
                predict(observation)

        memory_engine:
            Object providing:
                retrieve_all()
        """

        self.prediction_engine = (
            prediction_engine
            if prediction_engine is not None
            else None
        )

        self.memory_engine = (
            memory_engine
            if memory_engine is not None
            else None
        )

    def predict(
        self,
        observation
    ):
        """
        Generate a prediction.

        If no prediction engine is configured,
        the observation itself is used as the
        baseline prediction.

        Previous memories are then examined
        for a matching experience.
        """

        base_prediction = self._base_prediction(
            observation
        )

        memories = self._retrieve_memories()

        if len(memories) == 0:
            return base_prediction

        relevant = self._find_relevant_memory(
            observation,
            memories
        )

        if relevant is None:
            return base_prediction

        if "prediction" not in relevant:
            return base_prediction

        return relevant["prediction"]

    def predict_with_details(
        self,
        observation
    ):
        """
        Generate an adaptive prediction together
        with information about the experience
        used to produce it.
        """

        base_prediction = self._base_prediction(
            observation
        )

        memories = self._retrieve_memories()

        relevant = self._find_relevant_memory(
            observation,
            memories
        )

        if relevant is None:
            return {
                "status": "predicted",
                "prediction": base_prediction,
                "base_prediction": base_prediction,
                "experience_used": False,
                "experience": None
            }

        prediction = relevant.get(
            "prediction",
            base_prediction
        )

        return {
            "status": "predicted",
            "prediction": prediction,
            "base_prediction": base_prediction,
            "experience_used": True,
            "experience": dict(relevant)
        }

    def _base_prediction(
        self,
        observation
    ):
        """
        Generate the baseline prediction.
        """

        if self.prediction_engine is None:
            return observation

        predict = getattr(
            self.prediction_engine,
            "predict",
            None
        )

        if not callable(predict):
            return observation

        return predict(
            observation
        )

    def _retrieve_memories(self):
        """
        Retrieve stored experiences safely.

        Supports the existing MemoryEngine
        retrieve_all() interface.
        """

        if self.memory_engine is None:
            return []

        retrieve_all = getattr(
            self.memory_engine,
            "retrieve_all",
            None
        )

        if not callable(retrieve_all):
            return []

        try:
            memories = retrieve_all()

        except Exception:
            return []

        if not isinstance(
            memories,
            list
        ):
            return []

        return memories

    def _find_relevant_memory(
        self,
        observation,
        memories
    ):
        """
        Find the most recent relevant experience.

        Relevance is determined by matching
        the stored observation with the current
        observation.

        The search is performed from newest
        memory to oldest memory so the latest
        experience has priority.
        """

        for memory in reversed(
            memories
        ):

            if not isinstance(
                memory,
                dict
            ):
                continue

            if "observation" not in memory:
                continue

            if memory["observation"] != observation:
                continue

            if "prediction" not in memory:
                continue

            return memory

        return None

    def remember(
        self,
        observation,
        prediction,
        actual=None,
        difference=None,
        learning=None
    ):
        """
        Store a completed experience.

        The memory structure preserves:

        observation
        prediction
        actual
        difference
        learning
        """

        if self.memory_engine is None:
            return {
                "status": "unavailable",
                "reason": "memory_engine_not_configured"
            }

        store = getattr(
            self.memory_engine,
            "store",
            None
        )

        if not callable(store):
            return {
                "status": "rejected",
                "reason": "memory_engine_invalid"
            }

        memory = {
            "observation": observation,
            "prediction": prediction
        }

        if actual is not None:
            memory["actual"] = actual

        if difference is not None:
            memory["difference"] = difference

        if learning is not None:
            memory["learning"] = learning

        try:
            return store(
                memory
            )

        except Exception as error:
            return {
                "status": "failed",
                "reason": "memory_store_failed",
                "error": str(error)
            }

    def get_configuration(self):
        """
        Return the current adaptive prediction
        configuration.
        """

        return {
            "prediction_engine_configured": (
                self.prediction_engine is not None
            ),
            "memory_engine_configured": (
                self.memory_engine is not None
            )
        }
