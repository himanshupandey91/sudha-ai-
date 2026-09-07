"""
Sudha AI - Prediction Engine

Version 0.2

The prediction engine makes a prediction from an observation.

Version 0.2:
- Preserves the original observation-based prediction behavior.
- Supports optional hypothesis-aware prediction.
- Allows hypothesis predictions to be injected.
- Does not force a specific AI/ML model.
- Keeps backward compatibility with predict(observation).
"""


class PredictionEngine:

    def __init__(self, hypothesis_predictions=None):
        if hypothesis_predictions is None:
            hypothesis_predictions = {}

        if not isinstance(hypothesis_predictions, dict):
            raise ValueError(
                "hypothesis_predictions must be a dictionary"
            )

        for hypothesis, prediction in hypothesis_predictions.items():
            if not isinstance(hypothesis, str):
                raise ValueError(
                    "hypothesis names must be strings"
                )

            if not hypothesis:
                raise ValueError(
                    "hypothesis names must not be empty"
                )

            if not isinstance(prediction, (int, float)):
                raise ValueError(
                    "hypothesis predictions must be numeric"
                )

        self.hypothesis_predictions = dict(
            hypothesis_predictions
        )

    def predict(self, observation, hypothesis=None):
        """
        Generate a prediction from the current observation.

        Backward-compatible behavior:
        - Without a hypothesis, numeric observations are
          predicted using the current value as a baseline.
        - Other observations receive a simple fallback.

        Hypothesis-aware behavior:
        - If a hypothesis is supplied and a prediction exists
          for that hypothesis, the configured hypothesis
          prediction is returned.
        - Unknown hypotheses fall back to the original
          observation-based prediction.
        """

        if hypothesis is not None:
            name = self._get_hypothesis_name(
                hypothesis
            )

            if name in self.hypothesis_predictions:
                return self.hypothesis_predictions[name]

        if isinstance(observation, (int, float)):
            return observation

        return observation

    def _get_hypothesis_name(self, hypothesis):
        """
        Extract a hypothesis name from either:

        - a hypothesis dictionary
        - a hypothesis name string
        """

        if isinstance(hypothesis, dict):
            return hypothesis.get("hypothesis")

        if isinstance(hypothesis, str):
            return hypothesis

        return None

    def get_configuration(self):
        return {
            "hypothesis_predictions": dict(
                self.hypothesis_predictions
            )
        }
