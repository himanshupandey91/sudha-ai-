"""
Sudha AI - Adaptive Predictor

Version 0.1

Purpose:
    Learn future predictions from observed results.

Flow:

Prediction
    ↓
Actual Result
    ↓
Prediction Error
    ↓
Adaptive Update
    ↓
Better Future Prediction

This is a controlled learning component.
It does not claim general intelligence.
"""


class AdaptivePredictor:

    def __init__(self, learning_rate=0.5):
        if not isinstance(learning_rate, (int, float)):
            raise TypeError(
                "learning_rate must be numeric"
            )

        if not 0 < learning_rate <= 1:
            raise ValueError(
                "learning_rate must be greater than 0 and "
                "less than or equal to 1"
            )

        self.learning_rate = float(
            learning_rate
        )

        self.predictions = {}
        self.history = {}

    def predict(self, hypothesis):
        """
        Return the current prediction for a hypothesis.

        Returns None when the hypothesis has not
        been observed yet.
        """

        if not isinstance(hypothesis, str):
            raise ValueError(
                "hypothesis must be a string"
            )

        return self.predictions.get(
            hypothesis
        )

    def update(
        self,
        hypothesis,
        actual
    ):
        """
        Update prediction using the observed result.

        Formula:

        new_prediction =
            old_prediction
            + learning_rate
            * (actual - old_prediction)

        For a new hypothesis, the first prediction
        becomes the observed actual value.
        """

        if not isinstance(hypothesis, str):
            raise ValueError(
                "hypothesis must be a string"
            )

        if not hypothesis:
            raise ValueError(
                "hypothesis must not be empty"
            )

        if not isinstance(actual, (int, float)):
            raise ValueError(
                "actual must be numeric"
            )

        old_prediction = self.predictions.get(
            hypothesis
        )

        if old_prediction is None:
            new_prediction = float(actual)

        else:
            error = actual - old_prediction

            new_prediction = (
                old_prediction
                + self.learning_rate * error
            )

        self.predictions[
            hypothesis
        ] = new_prediction

        self.history.setdefault(
            hypothesis,
            []
        ).append(
            {
                "actual": actual,
                "prediction": new_prediction,
            }
        )

        return {
            "status": "updated",
            "hypothesis": hypothesis,
            "prediction": new_prediction,
            "actual": actual,
        }

    def get_history(self, hypothesis=None):
        if hypothesis is None:
            return {
                name: list(records)
                for name, records
                in self.history.items()
            }

        return list(
            self.history.get(
                hypothesis,
                []
            )
        )

    def clear(self):
        self.predictions.clear()
        self.history.clear()

        return {
            "status": "cleared"
        }

    def get_configuration(self):
        return {
            "learning_rate": self.learning_rate,
            "hypotheses": list(
                self.predictions.keys()
            ),
        }
