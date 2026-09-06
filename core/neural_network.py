"""
Sudha AI - Trainable Neural Network

Version 0.1

A small, deterministic, fully testable neural network.

Capabilities:
- Dense input layer
- One hidden layer
- ReLU activation
- Linear output layer
- Forward propagation
- Mean squared error
- Backpropagation
- Gradient descent
- Train on numeric examples
- Predict numeric outputs
- Bounded training

Design goals:
- No external dependencies
- Deterministic initialization
- Explicit validation
- No network access
- No external side effects
- Suitable for later integration with Sudha AI learning
"""


class NeuralNetwork:

    def __init__(
        self,
        input_size,
        hidden_size=8,
        output_size=1,
        learning_rate=0.01,
        seed=42
    ):
        """
        Create a trainable dense neural network.
        """

        if not isinstance(input_size, int):
            raise TypeError(
                "input_size must be an integer"
            )

        if input_size <= 0:
            raise ValueError(
                "input_size must be greater than zero"
            )

        if not isinstance(hidden_size, int):
            raise TypeError(
                "hidden_size must be an integer"
            )

        if hidden_size <= 0:
            raise ValueError(
                "hidden_size must be greater than zero"
            )

        if not isinstance(output_size, int):
            raise TypeError(
                "output_size must be an integer"
            )

        if output_size <= 0:
            raise ValueError(
                "output_size must be greater than zero"
            )

        if not isinstance(
            learning_rate,
            (int, float)
        ):
            raise TypeError(
                "learning_rate must be numeric"
            )

        if learning_rate <= 0:
            raise ValueError(
                "learning_rate must be greater than zero"
            )

        if not isinstance(seed, int):
            raise TypeError(
                "seed must be an integer"
            )

        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.learning_rate = float(
            learning_rate
        )
        self.seed = seed

        self._initialize_weights()

    def _initialize_weights(self):
        """
        Deterministically initialize network weights.

        A local pseudo-random generator is used so the
        network remains reproducible without external
        dependencies.
        """

        state = self.seed

        def random_value():
            nonlocal state

            state = (
                (state * 1664525 + 1013904223)
                % 4294967296
            )

            return (
                (state / 4294967296) * 2.0
            ) - 1.0

        self.weights_input_hidden = [
            [
                random_value() * 0.1
                for _ in range(self.hidden_size)
            ]
            for _ in range(self.input_size)
        ]

        self.bias_hidden = [
            0.0
            for _ in range(self.hidden_size)
        ]

        self.weights_hidden_output = [
            [
                random_value() * 0.1
                for _ in range(self.output_size)
            ]
            for _ in range(self.hidden_size)
        ]

        self.bias_output = [
            0.0
            for _ in range(self.output_size)
        ]

    def _validate_vector(
        self,
        values,
        expected_size,
        name
    ):
        """
        Validate a numeric vector.
        """

        if not isinstance(
            values,
            (list, tuple)
        ):
            raise TypeError(
                f"{name} must be a list or tuple"
            )

        if len(values) != expected_size:
            raise ValueError(
                f"{name} must contain "
                f"{expected_size} values"
            )

        for value in values:

            if not isinstance(
                value,
                (int, float)
            ):
                raise TypeError(
                    f"{name} values must be numeric"
                )

        return [
            float(value)
            for value in values
        ]

    def _relu(self, value):
        """
        ReLU activation.
        """

        return max(
            0.0,
            value
        )

    def _relu_derivative(self, value):
        """
        Derivative of ReLU.
        """

        if value > 0:
            return 1.0

        return 0.0

    def forward(self, inputs):
        """
        Run one forward pass.

        Returns:
            Network output.
        """

        inputs = self._validate_vector(
            inputs,
            self.input_size,
            "inputs"
        )

        hidden_pre_activation = []

        hidden_activation = []

        for hidden_index in range(
            self.hidden_size
        ):

            total = self.bias_hidden[
                hidden_index
            ]

            for input_index in range(
                self.input_size
            ):

                total += (
                    inputs[input_index]
                    * self.weights_input_hidden[
                        input_index
                    ][hidden_index]
                )

            hidden_pre_activation.append(
                total
            )

            hidden_activation.append(
                self._relu(total)
            )

        outputs = []

        for output_index in range(
            self.output_size
        ):

            total = self.bias_output[
                output_index
            ]

            for hidden_index in range(
                self.hidden_size
            ):

                total += (
                    hidden_activation[
                        hidden_index
                    ]
                    * self.weights_hidden_output[
                        hidden_index
                    ][output_index]
                )

            outputs.append(total)

        self._last_inputs = inputs
        self._last_hidden_pre_activation = (
            hidden_pre_activation
        )
        self._last_hidden_activation = (
            hidden_activation
        )
        self._last_outputs = outputs

        return outputs

    def predict(self, inputs):
        """
        Generate a prediction.

        Returns a single number when the network
        has one output, otherwise returns a list.
        """

        outputs = self.forward(
            inputs
        )

        if self.output_size == 1:
            return outputs[0]

        return outputs

    def loss(
        self,
        predicted,
        actual
    ):
        """
        Calculate mean squared error.
        """

        predicted = self._validate_vector(
            predicted,
            self.output_size,
            "predicted"
        )

        actual = self._validate_vector(
            actual,
            self.output_size,
            "actual"
        )

        total = 0.0

        for index in range(
            self.output_size
        ):

            error = (
                predicted[index]
                - actual[index]
            )

            total += error * error

        return (
            total
            / self.output_size
        )

    def train_step(
        self,
        inputs,
        actual
    ):
        """
        Perform one complete learning step.

        Flow:

            forward
              ↓
            error
              ↓
          backpropagation
              ↓
        weight update
        """

        inputs = self._validate_vector(
            inputs,
            self.input_size,
            "inputs"
        )

        actual = self._validate_vector(
            actual,
            self.output_size,
            "actual"
        )

        predicted = self.forward(
            inputs
        )

        error = [
            predicted[index]
            - actual[index]
            for index in range(
                self.output_size
            )
        ]

        loss = self.loss(
            predicted,
            actual
        )

        output_gradients = [
            (
                2.0
                * error[index]
                / self.output_size
            )
            for index in range(
                self.output_size
            )
        ]

        hidden_gradients = [
            0.0
            for _ in range(
                self.hidden_size
            )
        ]

        for hidden_index in range(
            self.hidden_size
        ):

            gradient = 0.0

            for output_index in range(
                self.output_size
            ):

                gradient += (
                    output_gradients[
                        output_index
                    ]
                    * self.weights_hidden_output[
                        hidden_index
                    ][output_index]
                )

            hidden_gradients[
                hidden_index
            ] = (
                gradient
                * self._relu_derivative(
                    self._last_hidden_pre_activation[
                        hidden_index
                    ]
                )
            )

        for hidden_index in range(
            self.hidden_size
        ):

            for output_index in range(
                self.output_size
            ):

                gradient = (
                    self._last_hidden_activation[
                        hidden_index
                    ]
                    * output_gradients[
                        output_index
                    ]
                )

                self.weights_hidden_output[
                    hidden_index
                ][output_index] -= (
                    self.learning_rate
                    * gradient
                )

        for output_index in range(
            self.output_size
        ):

            self.bias_output[
                output_index
            ] -= (
                self.learning_rate
                * output_gradients[
                    output_index
                ]
            )

        for input_index in range(
            self.input_size
        ):

            for hidden_index in range(
                self.hidden_size
            ):

                gradient = (
                    self._last_inputs[
                        input_index
                    ]
                    * hidden_gradients[
                        hidden_index
                    ]
                )

                self.weights_input_hidden[
                    input_index
                ][hidden_index] -= (
                    self.learning_rate
                    * gradient
                )

        for hidden_index in range(
            self.hidden_size
        ):

            self.bias_hidden[
                hidden_index
            ] -= (
                self.learning_rate
                * hidden_gradients[
                    hidden_index
                ]
            )

        return {
            "loss": loss,
            "prediction": (
                predicted[0]
                if self.output_size == 1
                else predicted
            )
        }

    def train(
        self,
        inputs,
        actual,
        epochs=100
    ):
        """
        Train the network on one example
        for a bounded number of epochs.
        """

        if not isinstance(
            epochs,
            int
        ):
            raise TypeError(
                "epochs must be an integer"
            )

        if epochs <= 0:
            raise ValueError(
                "epochs must be greater than zero"
            )

        history = []

        for _ in range(epochs):

            result = self.train_step(
                inputs,
                actual
            )

            history.append(
                result["loss"]
            )

        return {
            "status": "trained",
            "epochs": epochs,
            "initial_loss": history[0],
            "final_loss": history[-1],
            "loss_history": history
        }

    def get_parameters(self):
        """
        Return a copy of the current network parameters.
        """

        return {
            "weights_input_hidden": [
                row.copy()
                for row in self.weights_input_hidden
            ],
            "bias_hidden": (
                self.bias_hidden.copy()
            ),
            "weights_hidden_output": [
                row.copy()
                for row in self.weights_hidden_output
            ],
            "bias_output": (
                self.bias_output.copy()
            )
        }

    def get_configuration(self):
        """
        Return network configuration.
        """

        return {
            "input_size": self.input_size,
            "hidden_size": self.hidden_size,
            "output_size": self.output_size,
            "learning_rate": self.learning_rate,
            "seed": self.seed
      }
