"""
Sudha AI - Evaluation Engine

Version 0.1

Evaluates experiment results and determines
which hypothesis performed better.

Design goals:
- Deterministic evaluation
- Explicit scoring
- No external side effects
- Fully testable
"""


class EvaluationEngine:

    def evaluate(self, experiment_result):
        """
        Evaluate one experiment result.

        Lower predicted_difference means
        better expected performance.
        """

        if not isinstance(experiment_result, dict):
            raise TypeError(
                "experiment_result must be a dictionary"
            )

        result = experiment_result.get("result")

        if not isinstance(result, dict):
            return {
                "status": "rejected",
                "reason": "result_must_be_a_dictionary"
            }

        predicted_difference = result.get(
            "predicted_difference"
        )

        if not isinstance(
            predicted_difference,
            (int, float)
        ):
            return {
                "status": "rejected",
                "reason": "predicted_difference_must_be_numeric"
            }

        return {
            "status": "evaluated",
            "hypothesis": experiment_result.get(
                "hypothesis"
            ),
            "predicted_difference": predicted_difference,
            "score": -predicted_difference
        }

    def better(self, first_result, second_result):
        """
        Compare two evaluated results.

        Returns True when first_result is better.
        """

        if not isinstance(first_result, dict):
            raise TypeError(
                "first_result must be a dictionary"
            )

        if not isinstance(second_result, dict):
            raise TypeError(
                "second_result must be a dictionary"
            )

        first_difference = first_result.get(
            "predicted_difference"
        )

        second_difference = second_result.get(
            "predicted_difference"
        )

        if not isinstance(
            first_difference,
            (int, float)
        ):
            return False

        if not isinstance(
            second_difference,
            (int, float)
        ):
            return True

        return first_difference < second_difference
