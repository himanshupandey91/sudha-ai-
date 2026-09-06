"""
Sudha AI - Adaptive Prediction Engine

Version 0.4

Uses previous experience to adapt future predictions.

Core behavior:

Current Observation
        ↓
Base Prediction
        ↓
Previous Experiences
        ↓
Prediction Errors
        ↓
Average Error
        ↓
Adaptive Prediction

Design goals:
- Use previous experience
- Learn from prediction error
- Support average historical error
- Preserve exact-match experience behavior
- Backward-compatible interfaces
- Deterministic behavior
- No external side effects
"""


from core.prediction import PredictionEngine
from core.memory import MemoryEngine


class AdaptivePredictionEngine:

    def __init__(
        self,
        prediction_engine=None,
        memory_engine=None
    ):
        """
        Initialize the adaptive prediction engine.
        """

        self.prediction_engine = (
            prediction_engine
            if prediction_engine is not None
            else PredictionEngine()
        )

        self.memory_engine = (
            memory_engine
            if memory_engine is not None
            else MemoryEngine()
        )

    def predict(self, observation):
        """
        Generate an adaptive prediction.

        Behavior:

        1. Generate the normal/base prediction.
        2. Look at previous experiences.
        3. Calculate the average historical error.
        4. Apply that error to numeric predictions.
        5. If an exact previous observation exists,
           use its learned prediction directly.
        """

        base_prediction = self._base_prediction(
            observation
        )

        memories = self._retrieve_memories()

        # First preference:
        # exact previous experience.
        relevant_memory = self._find_relevant_memory(
            observation,
            memories
        )

        if relevant_memory is not None:

            previous_prediction = (
                relevant_memory.get("prediction")
            )

            difference = (
                relevant_memory.get("difference")
            )

            if (
                isinstance(
                    previous_prediction,
                    (int, float)
                )
                and isinstance(
                    difference,
                    (int, float)
                )
                and isinstance(
                    base_prediction,
                    (int, float)
                )
            ):
                return (
                    base_prediction
                    + difference
                )

            if previous_prediction is not None:
                return previous_prediction

        # No exact experience:
        # use historical average error.
        average_error = self._average_error(
            memories
        )

        if isinstance(
            base_prediction,
            (int, float)
        ) and average_error is not None:

            return (
                base_prediction
                + average_error
            )

        return base_prediction

    def predict_with_details(
        self,
        observation
    ):
        """
        Generate an adaptive prediction with
        diagnostic information.
        """

        base_prediction = self._base_prediction(
            observation
        )

        memories = self._retrieve_memories()

        relevant_memory = self._find_relevant_memory(
            observation,
            memories
        )

        average_error = self._average_error(
            memories
        )

        prediction = self.predict(
            observation
        )

        return {
            "status": "predicted",
            "observation": observation,
            "base_prediction": base_prediction,
            "prediction": prediction,
            "experience_used": (
                relevant_memory is not None
            ),
            "experience": (
                dict(relevant_memory)
                if relevant_memory is not None
                else None
            ),
            "average_error": average_error
        }

    def remember(
        self,
        observation,
        prediction,
        actual=None,
        difference=None,
        learning=None
    ):
        """
        Store a new experience in memory.
        """

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

        return self.memory_engine.store(
            memory
        )

    def _base_prediction(
        self,
        observation
    ):
        """
        Generate the normal prediction.
        """

        return self.prediction_engine.predict(
            observation
        )

    def _retrieve_memories(self):
        """
        Retrieve memories using the supported
        memory interface.
        """

        retrieve_all = getattr(
            self.memory_engine,
            "retrieve_all",
            None
        )

        if callable(retrieve_all):
            memories = retrieve_all()

        else:
            retrieve = getattr(
                self.memory_engine,
                "retrieve",
                None
            )

            if callable(retrieve):
                memories = retrieve()

            else:
                memories = []

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
        Find the most recent exact-match
        experience for the observation.
        """

        for memory in reversed(
            memories
        ):

            if not isinstance(
                memory,
                dict
            ):
                continue

            if memory.get(
                "observation"
            ) == observation:

                return memory

        return None

    def _average_error(
        self,
        memories
    ):
        """
        Calculate the average historical
        prediction error.

        Only numeric differences are used.
        """

        errors = []

        for memory in memories:

            if not isinstance(
                memory,
                dict
            ):
                continue

            difference = memory.get(
                "difference"
            )

            if isinstance(
                difference,
                (int, float)
            ):
                errors.append(
                    difference
                )

        if len(errors) == 0:
            return None

        return sum(errors) / len(errors)

    def get_configuration(self):
        """
        Return engine configuration.
        """

        return {
            "prediction_engine": (
                type(
                    self.prediction_engine
                ).__name__
            ),
            "memory_engine": (
                type(
                    self.memory_engine
                ).__name__
            ),
            "memory_size": (
                self.memory_engine.size()
                if hasattr(
                    self.memory_engine,
                    "size"
                )
                else None
            )
                    }
