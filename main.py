from sudha_runtime import SudhaRuntime


class SimpleEnvironment:
    """
    Demo environment.

    IMPORTANT:
    The predictor does not receive the hidden target directly.
    """

    def __init__(self):
        self.state = 10.0
        self.hidden_drift = 1.5

    def observe(self):
        return self.state

    def step(self, action):
        if action == "increase":
            self.state += self.hidden_drift + 1.0

        elif action == "decrease":
            self.state += self.hidden_drift - 1.0

        else:
            self.state += self.hidden_drift

        return self.state


class AdaptivePredictor:
    """
    Very small online-learning predictor.

    It learns the average change between
    prediction and actual outcome.
    """

    def __init__(self):
        self.bias = 0.0
        self.learning_rate = 0.2

    def predict(self, observation):
        return observation + self.bias + 1.5

    def update(
        self,
        observation,
        action,
        prediction,
        actual,
        error,
    ):
        delta = float(actual) - float(prediction)

        self.bias += self.learning_rate * delta


class ActionEngine:
    """
    Chooses actions using the current prediction.
    """

    def select_action(self, observation, prediction):
        difference = prediction - observation

        if difference > 1.5:
            return "decrease"

        if difference < 1.0:
            return "increase"

        return "hold"


def main():
    environment = SimpleEnvironment()
    predictor = AdaptivePredictor()
    action_engine = ActionEngine()

    runtime = SudhaRuntime(
        environment=environment,
        predictor=predictor,
        action_engine=action_engine,
        persistence_path="sudha_runtime_memory.json",
    )

    print("=" * 60)
    print("SUDHA AI - CLOSED AUTONOMOUS COGNITIVE LOOP")
    print("=" * 60)

    runtime.run(cycles=100)

    print("=" * 60)
    print("Closed loop finished.")
    print(f"Total cycles: {runtime.cycle_count}")
    print("=" * 60)


if __name__ == "__main__":
    main()
