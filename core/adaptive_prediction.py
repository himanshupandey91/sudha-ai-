"""
Sudha AI - Adaptive Prediction Engine

Version 0.7

Uses previous experience to adapt future predictions.

Prediction flow:

Current Observation
        ↓
Base Prediction
        ↓
Hierarchical Memory
        ↓
Relevant Previous Experience
        ↓
Observed Actual Outcome
        ↓
Adaptive Prediction

Compatibility:
- Preserves existing MemoryEngine behavior
- Supports optional HierarchicalMemory
- Uses exact observation matching
- Supports numeric predictions
- Supports structured predictions
- Uses actual outcomes when available
- Uses prediction error only as a fallback
- HierarchicalMemory has priority over legacy MemoryEngine
- Avoids duplicate historical error counting
- Deterministic behavior
- No external side effects
"""

from core.prediction import PredictionEngine
from core.memory import MemoryEngine


class AdaptivePredictionEngine:

    def __init__(
        self,
        prediction_engine=None,
        memory_engine=None,
        hierarchical_memory=None
    ):
        """
        Initialize the adaptive prediction engine.

        MemoryEngine remains supported for backward compatibility.

        HierarchicalMemory is optional and, when supplied,
        becomes the preferred source of previous experience.
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

        self.hierarchical_memory = (
            hierarchical_memory
        )

    def predict(self, observation):
        """
        Generate an adaptive prediction.

        Priority:

        1. Generate base prediction.
        2. Search HierarchicalMemory.
        3. Use the most recent matching hierarchical experience.
        4. Search compatibility MemoryEngine.
        5. Use the most recent matching legacy experience.
        6. Use historical average error for numeric predictions.
        7. Return the base prediction.

        HierarchicalMemory is preferred because it is the
        structured memory system.
        """

        base_prediction = self._base_prediction(
            observation
        )

        hierarchical_memories = (
            self._retrieve_hierarchical_memories(
                observation
            )
        )

        relevant_memory = (
            self._find_relevant_memory(
                observation,
                hierarchical_memories
            )
        )

        if relevant_memory is not None:
            prediction = self._prediction_from_memory(
                base_prediction,
                relevant_memory
            )

            if prediction is not None:
                return prediction

        memories = self._retrieve_memories()

        relevant_memory = (
            self._find_relevant_memory(
                observation,
                memories
            )
        )

        if relevant_memory is not None:
            prediction = self._prediction_from_memory(
                base_prediction,
                relevant_memory
            )

            if prediction is not None:
                return prediction

        average_error = self._average_error(
            memories
        )

        if (
            isinstance(
                base_prediction,
                (int, float)
            )
            and average_error is not None
        ):
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

        hierarchical_memories = (
            self._retrieve_hierarchical_memories(
                observation
            )
        )

        relevant_hierarchical_memory = (
            self._find_relevant_memory(
                observation,
                hierarchical_memories
            )
        )

        memories = self._retrieve_memories()

        relevant_legacy_memory = (
            self._find_relevant_memory(
                observation,
                memories
            )
        )

        prediction = self.predict(
            observation
        )

        experience = (
            relevant_hierarchical_memory
            if relevant_hierarchical_memory is not None
            else relevant_legacy_memory
        )

        return {
            "status": "predicted",
            "observation": observation,
            "base_prediction": base_prediction,
            "prediction": prediction,
            "experience_used": (
                experience is not None
            ),
            "experience_source": (
                "hierarchical_memory"
                if relevant_hierarchical_memory is not None
                else (
                    "memory_engine"
                    if relevant_legacy_memory is not None
                    else None
                )
            ),
            "experience": (
                dict(experience)
                if experience is not None
                else None
            ),
            "average_error": self._average_error(
                memories
            )
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
        Store a new experience in the
        compatibility MemoryEngine.

        HierarchicalMemory storage is handled by
        ExperienceLearningEngine so that one experience
        is not written twice.
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
        Retrieve memories from the compatibility
        MemoryEngine.
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

    def _retrieve_hierarchical_memories(
        self,
        observation
    ):
        """
        Retrieve relevant episodic experiences from
        HierarchicalMemory.

        Exact matching is intentionally used for
        this integration stage.
        """

        if self.hierarchical_memory is None:
            return []

        retrieve_matching = getattr(
            self.hierarchical_memory,
            "retrieve_episodic_matching",
            None
        )

        if not callable(
            retrieve_matching
        ):
            return []

        try:
            memories = retrieve_matching(
                {
                    "observation": observation
                }
            )
        except (
            TypeError,
            ValueError
        ):
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
        Find the most recent exact-match
        experience for the observation.
        """

        if not isinstance(
            memories,
            list
        ):
            return None

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

    def _prediction_from_memory(
        self,
        base_prediction,
        memory
    ):
        """
        Convert previous experience into
        an adaptive prediction.

        Priority:

        1. Use observed actual outcome when available.
        2. Adapt structured predictions using actual outcome.
        3. Use numeric error correction when actual
           outcome is unavailable.
        4. Fall back to previous prediction.

        Important:

        `difference` is normally an absolute error.

        Therefore:

            difference = abs(actual - prediction)

        cannot safely determine the direction of correction.

        When `actual` exists, it is the authoritative
        observed target and must be preferred.
        """

        if not isinstance(
            memory,
            dict
        ):
            return None

        previous_prediction = memory.get(
            "prediction"
        )

        actual = memory.get(
            "actual"
        )

        difference = memory.get(
            "difference"
        )

        # -------------------------------------------------
        # Case 1: Numeric actual outcome
        # -------------------------------------------------

        if isinstance(
            actual,
            (int, float)
        ):
            if isinstance(
                base_prediction,
                (int, float)
            ):
                return actual

            if (
                isinstance(
                    base_prediction,
                    dict
                )
                and isinstance(
                    previous_prediction,
                    dict
                )
            ):
                structured_prediction = dict(
                    base_prediction
                )

                if (
                    "value" in structured_prediction
                    and isinstance(
                        structured_prediction["value"],
                        (int, float)
                    )
                ):
                    structured_prediction[
                        "value"
                    ] = actual

                    return structured_prediction

        # -------------------------------------------------
        # Case 2: Structured actual outcome
        # -------------------------------------------------

        if (
            isinstance(
                base_prediction,
                dict
            )
            and isinstance(
                previous_prediction,
                dict
            )
            and isinstance(
                actual,
                dict
            )
        ):
            if self._has_numeric_overlap(
                base_prediction,
                actual
            ):
                structured_prediction = dict(
                    base_prediction
                )

                for key, value in actual.items():
                    if (
                        key in structured_prediction
                        and isinstance(
                            value,
                            (int, float)
                        )
                    ):
                        structured_prediction[
                            key
                        ] = value

                return structured_prediction

        # -------------------------------------------------
        # Case 3: Numeric prediction + numeric difference
        # -------------------------------------------------

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

        # -------------------------------------------------
        # Case 4: Previous learned prediction
        # -------------------------------------------------

        if previous_prediction is not None:
            return previous_prediction

        return None

    def _has_numeric_overlap(
        self,
        base_prediction,
        actual
    ):
        """
        Check whether two dictionaries contain at least
        one shared numeric field.
        """

        if not isinstance(
            base_prediction,
            dict
        ):
            return False

        if not isinstance(
            actual,
            dict
        ):
            return False

        for key, value in actual.items():
            if (
                key in base_prediction
                and isinstance(
                    base_prediction[key],
                    (int, float)
                )
                and isinstance(
                    value,
                    (int, float)
                )
            ):
                return True

        return False

    def _average_error(
        self,
        memories
    ):
        """
        Calculate the average historical
        prediction error.

        Only numeric differences are used.
        """

        if not isinstance(
            memories,
            list
        ):
            return None

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

        return (
            sum(errors)
            / len(errors)
        )

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
            "hierarchical_memory": (
                type(
                    self.hierarchical_memory
                ).__name__
                if self.hierarchical_memory is not None
                else None
            ),
            "memory_size": (
                self.memory_engine.size()
                if hasattr(
                    self.memory_engine,
                    "size"
                )
                else None
            ),
            }
