"""
Sudha AI - Prediction Engine

The prediction engine makes a prediction from an observation.
Version 0.1 uses a simple baseline predictor.

This is intentionally simple.
Later versions can replace this with a trained model.
"""


class PredictionEngine:

    def predict(self, observation):
        """
        Generate a prediction from the current observation.

        Version 0.1:
        - Numeric observations are predicted using the
          current value as a baseline.
        - Other observations receive a simple fallback.
        """

        if isinstance(observation, (int, float)):
            return observation

        return observation
