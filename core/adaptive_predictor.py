"""
Sudha AI - Adaptive Predictor (EDUCATIONAL VERSION)

Version 0.2 - SIMPLIFIED IMPLEMENTATION

WARNING:
────────
This is NOT a real machine learning implementation.
It uses basic linear math, not neural networks.

What this does:
├─ Stores predictions per hypothesis
├─ Updates using: new_pred = old_pred + learning_rate × error
├─ Very simple linear interpolation
└─ Good for learning concepts

What this doesn't do:
├─ Neural networks
├─ Non-linear transformations
├─ Proper optimization
├─ Regularization
├─ Real learning
└─ Actual intelligence

For a REAL adaptive predictor, you'd use:
├─ PyTorch or TensorFlow
├─ Multiple layers
├─ Backpropagation
├─ Activation functions (ReLU, sigmoid, etc.)
├─ Optimizers (Adam, SGD, etc.)
└─ Proper training pipelines

This uses:
└─ High school algebra only
"""


class AdaptivePredictor:
    """
    EDUCATIONAL: Simple linear prediction updater
    
    NOT a real ML model.
    Just demonstrates the concept of error-driven updates.
    """

    def __init__(self, learning_rate=0.5):
        """
        Initialize predictor.
        
        Args:
            learning_rate: How much to adjust predictions (0-1)
                          Higher = faster learning, more instability
                          Lower = slower learning, more stable
        
        NOTE: Real ML uses sophisticated schedules for this.
        This just uses a fixed value.
        """
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

        # Stores predictions: {hypothesis_name: prediction_value}
        self.predictions = {}
        
        # Stores history: {hypothesis_name: [{actual, prediction, error}, ...]}
        self.history = {}
        
        # Honest note:
        print(
            "\n⚠️  WARNING: This is an EDUCATIONAL predictor.\n"
            "   It uses BASIC LINEAR MATH, NOT real machine learning.\n"
            "   For actual ML, use PyTorch or TensorFlow.\n"
        )

    def predict(self, hypothesis):
        """
        Return the current prediction for a hypothesis.

        Returns None when no prediction exists.
        
        NOTE: This just looks up a stored value.
        Real ML would run data through neural network layers.
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
        
        LIMITATION: This is just manual initialization.
        Real systems would learn initial values.
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

        Formula (VERY BASIC):

        error = actual - old_prediction
        new_prediction = old_prediction + learning_rate * error
        
        IMPORTANT:
        This is a 1990s algorithm.
        Modern ML uses:
        ├─ Backpropagation through layers
        ├─ Activation functions
        ├─ Complex optimization
        ├─ Regularization
        └─ Many other techniques
        
        This just uses: new = old + slope * error
        
        Example:
        old prediction = 10
        actual = 20
        learning rate = 0.5
        error = 20 - 10 = 10
        new prediction = 10 + (0.5 * 10) = 15
        
        Is this learning? Kind of, but very limited.
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
            # First time: just use actual as prediction
            new_prediction = float(
                actual
            )
            error = None
        else:
            # Calculate error
            error = (
                actual
                - old_prediction
            )
            # Update: move toward actual by learning_rate proportion
            new_prediction = (
                old_prediction
                + self.learning_rate * error
            )

        # Store new prediction
        self.predictions[
            hypothesis
        ] = new_prediction

        # Record in history
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
            "error": error,
            "note": "This is a simple linear update, not real ML"
        }

    def get_history(
        self,
        hypothesis=None
    ):
        """Get update history for a hypothesis."""
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
        """Clear all predictions and history."""
        self.predictions.clear()
        self.history.clear()

        return {
            "status": "cleared"
        }

    def get_configuration(self):
        """Get current configuration."""
        return {
            "learning_rate": self.learning_rate,
            "hypotheses": list(
                self.predictions.keys()
            ),
            "note": "This is an EDUCATIONAL system, not real ML"
        }
