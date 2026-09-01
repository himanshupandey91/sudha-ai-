"""
Difference Module

Measures the difference between what the AI predicted
and what actually happened.
"""


class DifferenceEngine:

    def calculate(self, prediction, actual):
        """
        Calculate prediction error.

        Returns:
            Numeric difference between prediction and reality.
        """

        if isinstance(prediction, (int, float)) and isinstance(actual, (int, float)):
            return abs(actual - prediction)

        if prediction == actual:
            return 0

        return 1
