"""
Sudha AI - Adaptive Prediction Engine

Version 0.1

Uses previous experiences from memory to
adjust future predictions.

Design goals:
- Deterministic behavior
- Explicit adaptation
- Bounded adjustment
- No external side effects
- Fully testable
"""


class AdaptivePredictionEngine:

    def __init__(self, base_predictor, memory_engine):
        """
        Initialize the adaptive predictor.

        base_predictor:
            Existing PredictionEngine.

        memory_engine:
            Sudha AI MemoryEngine.
        """

        self.base_predictor = base_predictor
        self.memory = memory_engine

    def predict(self, observation):
        """
        Generate a prediction using:

        current observation
        +
        previous prediction errors
        """

        base_prediction = self.base_predictor.predict(
            observation
        )

        memories = self.memory.retrieve_all()

        if not memories:
            return base_prediction

        numeric_errors = []

        for memory in memories:

            difference = memory.get("difference")

            if isinstance(difference, (int, float)):
                numeric_errors.append(difference)

        if not numeric_errors:
            return base_prediction

        average_error = sum(numeric_errors) / len(numeric_errors)

        if isinstance(base_prediction, (int, float)):
            return base_prediction + average_error

        return base_prediction
