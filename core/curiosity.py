"""
Sudha AI - Curiosity Module

Version 0.1

Generates curiosity from prediction error.
"""


class CuriosityEngine:

    def calculate(self, difference):
        """
        Convert prediction error into curiosity.

        Larger prediction error = stronger curiosity.
        """

        if difference < 0:
            difference = abs(difference)

        return {
            "difference": difference,
            "curiosity": difference
        }
