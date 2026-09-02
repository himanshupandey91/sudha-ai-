"""
Sudha AI - Learning Module

Version 0.1

Converts prediction error into a learning signal.
"""


class LearningEngine:

    def learn(self, difference):
        """
        Convert prediction error into a learning signal.

        Larger error = stronger learning signal.
        """

        if difference < 0:
            difference = abs(difference)

        return {
            "error": difference,
            "learning_signal": difference
        }
