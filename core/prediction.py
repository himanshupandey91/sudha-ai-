"""
Sudha AI - Prediction Engine

Version 0.3

The prediction engine makes predictions from observations
and can optionally learn from observed results.

Version 0.3:
- Preserves legacy observation-based prediction.
- Preserves static hypothesis predictions.
- Supports AdaptivePredictor integration.
- Uses learned predictions when available.
- Provides a learning boundary for observed results.
- Keeps backward compatibility with predict(observation).
- Does not force a specific AI/ML model.
"""


class PredictionEngine:

    def __init__(
        self,
        hypothesis_predictions=None,
        adaptive_predictor=None
    ):
        if hypothesis_predictions is None:
            hypothesis_predictions = {}

        if not isinstance(
            hypothesis_predictions,
            dict
        ):
            raise ValueError(
                "hypothesis_predictions must be a dictionary"
            )

        for hypothesis, prediction in (
            hypothesis_predictions.items()
        ):
            if not isinstance(
                hypothesis,
                str
            ):
                raise ValueError(
                    "hypothesis names must be strings"
                )

            if not hypothesis:
                raise ValueError(
                    "hypothesis names must not be empty"
                )

            if not isinstance(
                prediction,
                (int, float)
            ):
                raise ValueError(
                    "hypothesis predictions must be numeric"
                )

        if adaptive_predictor is not None:

            predictor = getattr(
                adaptive_predictor,
                "predict",
                None
            )

            updater = getattr(
                adaptive_predictor,
                "update",
                None
            )

            if not callable(predictor):
                raise ValueError(
                    "adaptive_predictor must provide "
                    "a callable predict method"
                )

            if not callable(updater):
                raise ValueError(
                    "adaptive_predictor must provide "
                    "a callable update method"
                )

        self.hypothesis_predictions = dict(
            hypothesis_predictions
        )

        self.adaptive_predictor = (
            adaptive_predictor
        )

    def predict(
        self,
        observation,
        hypothesis=None
    ):
        """
        Generate a prediction.

        Priority:

        1. Learned adaptive prediction
        2. Static hypothesis prediction
        3. Original observation fallback
        """

        if hypothesis is not None:

            name = self._get_hypothesis_name(
                hypothesis
            )

            if name is not None:

                if self.adaptive_predictor is not None:

                    learned_prediction = (
                        self.adaptive_predictor.predict(
                            name
                        )
                    )

                    if learned_prediction is not None:
                        return learned_prediction

                if name in self.hypothesis_predictions:
                    return self.hypothesis_predictions[
                        name
                    ]

        if isinstance(
            observation,
            (int, float)
        ):
            return observation

        return observation

    def learn(
        self,
        hypothesis,
        actual
    ):
        """
        Learn from an observed actual result.

        The result is delegated to AdaptivePredictor
        when adaptive learning is enabled.
        """

        if self.adaptive_predictor is None:
            return {
                "status": "unavailable",
                "reason": "adaptive_predictor_not_configured"
            }

        name = self._get_hypothesis_name(
            hypothesis
        )

        if name is None:
            return {
                "status": "failed",
                "reason": "invalid_hypothesis"
            }

        try:
            result = self.adaptive_predictor.update(
                name,
                actual
            )

        except Exception as error:
            return {
                "status": "failed",
                "reason": "adaptive_learning_failed",
                "error": str(error)
            }

        return {
            "status": "learned",
            "hypothesis": name,
            "result": result
        }

    def update_from_actual(
        self,
        hypothesis,
        actual
    ):
        """
        Alias for learn().

        Provides an explicit boundary for connecting
        observed results to adaptive prediction.
        """

        return self.learn(
            hypothesis,
            actual
        )

    def _get_hypothesis_name(
        self,
        hypothesis
    ):
        """
        Extract a hypothesis name from either:

        - a hypothesis dictionary
        - a hypothesis name string
        """

        if isinstance(
            hypothesis,
            dict
        ):
            return hypothesis.get(
                "hypothesis"
            )

        if isinstance(
            hypothesis,
            str
        ):
            return hypothesis

        return None

    def get_configuration(self):
        configuration = {
            "hypothesis_predictions": dict(
                self.hypothesis_predictions
            ),
            "adaptive_predictor": (
                type(
                    self.adaptive_predictor
                ).__name__
                if self.adaptive_predictor is not None
                else None
            )
        }

        return configuration
