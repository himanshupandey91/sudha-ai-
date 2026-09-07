"""
Sudha AI - Adaptive Predictor

Version 0.2

Purpose:
    Learn future predictions from observed results.

Learning flow:

Initial Prediction
    ↓
Actual Result
    ↓
Prediction Error
    ↓
Learning Rate
    ↓
Updated Prediction

This is a controlled adaptive prediction component.
It does not claim general intelligence.
"""


class AdaptivePredictor:

    def __init__(self, learning_rate=0.5):
        if not isinstance(
            learning_rate,
            (int, float)
        ):
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

        Returns None when no prediction exists.
        """

        if not isinstance(
            hypothesis,
            str
        ):
            raise ValueError(
                "hypothesis must be a string"
            )

        return self.predictions.get(
            hypothesis
        )

    def set_prediction(
        self,
        hypothesis,
        prediction
    ):
        """
        Seed an initial prediction.

        This allows the adaptive predictor to start
        from an existing prediction instead of treating
        the first observed actual result as the prediction.
        """

        if not isinstance(
            hypothesis,
            str
        ):
            raise ValueError(
                "hypothesis must be a string"
            )

        if not hypothesis:
            raise ValueError(
                "hypothesis must not be empty"
            )

        if not isinstance(
            prediction,
            (int, float)
        ):
            raise ValueError(
                "prediction must be numeric"
            )

        self.predictions[
            hypothesis
        ] = float(prediction)

        return {
            "status": "seeded",
            "hypothesis": hypothesis,
            "prediction": float(prediction)
        }

    def update(
        self,
        hypothesis,
        actual
    ):
        """
        Update prediction using the observed result.

        Formula:

        error =
            actual - old_prediction

        new_prediction =
            old_prediction
            + learning_rate * error

        If no initial prediction exists, the first
        actual result becomes the initial prediction.

        Example:

        old prediction = 10
        actual = 20
        learning rate = 0.5

        error = 20 - 10 = 10

        new prediction =
            10 + (0.5 * 10)
            = 15
        """

        if not isinstance(
            hypothesis,
            str
        ):
            raise ValueError(
                "hypothesis must be a string"
            )

        if not hypothesis:
            raise ValueError(
                "hypothesis must not be empty"
            )

        if not isinstance(
            actual,
            (int, float)
        ):
            raise ValueError(
                "actual must be numeric"
            )

        old_prediction = self.predictions.get(
            hypothesis
        )

        if old_prediction is None:

            new_prediction = float(
                actual
            )

            error = None

        else:

            error = (
                actual
                - old_prediction
            )

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
                "error": error
            }
        )

        return {
            "status": "updated",
            "hypothesis": hypothesis,
            "prediction": new_prediction,
            "actual": actual,
            "error": error
        }

    def get_history(
        self,
        hypothesis=None
    ):
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
