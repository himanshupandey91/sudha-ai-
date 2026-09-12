from core.adaptive_predictor import AdaptivePredictor


class EnvironmentA:
    def __init__(self):
        self.temperature = 20.0

    def step(self, action):
        before = self.temperature

        if action == "increase_temperature":
            self.temperature += 1.0
        elif action == "decrease_temperature":
            self.temperature -= 1.0
        else:
            raise ValueError(f"Unknown action: {action}")

        return {
            "before_temperature": before,
            "actual_temperature": self.temperature,
            "actual_effect": self.temperature - before,
        }


class EnvironmentB:
    def __init__(self):
        self.temperature = 20.0

    def step(self, action):
        before = self.temperature

        if action == "increase_temperature":
            self.temperature += 2.0
        elif action == "decrease_temperature":
            self.temperature -= 2.0
        else:
            raise ValueError(f"Unknown action: {action}")

        return {
            "before_temperature": before,
            "actual_temperature": self.temperature,
            "actual_effect": self.temperature - before,
        }


def test_learned_prediction_transfers_to_new_environment():
    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    hypothesis = "effect_of_increase_temperature"

    predictor.set_prediction(
        hypothesis=hypothesis,
        prediction=0.0
    )

    environment_a = EnvironmentA()

    for _ in range(10):
        result = environment_a.step(
            "increase_temperature"
        )

        predictor.update(
            hypothesis=hypothesis,
            actual=result["actual_effect"]
        )

    learned_in_environment_a = predictor.predict(
        hypothesis
    )

    assert abs(
        learned_in_environment_a - 1.0
    ) < 0.01

    environment_b = EnvironmentB()

    result_b = environment_b.step(
        "increase_temperature"
    )

    old_prediction = predictor.predict(
        hypothesis
    )

    assert old_prediction != result_b["actual_effect"]

    prediction_error = abs(
        result_b["actual_effect"] - old_prediction
    )

    assert prediction_error > 0.5

    predictor.update(
        hypothesis=hypothesis,
        actual=result_b["actual_effect"]
    )

    updated_prediction = predictor.predict(
        hypothesis
    )

    assert updated_prediction > old_prediction

    # Allow a small numerical/quantization tolerance.
    assert abs(
        updated_prediction - 1.5
    ) < 0.001


def test_new_environment_knowledge_is_corrected_by_actual_result():
    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    hypothesis = "effect_of_increase_temperature"

    predictor.set_prediction(
        hypothesis=hypothesis,
        prediction=1.0
    )

    environment_b = EnvironmentB()

    errors = []

    for _ in range(10):
        prediction = predictor.predict(
            hypothesis
        )

        result = environment_b.step(
            "increase_temperature"
        )

        actual = result["actual_effect"]

        error = abs(
            actual - prediction
        )

        errors.append(error)

        predictor.update(
            hypothesis=hypothesis,
            actual=actual
        )

    assert errors[0] == 1.0

    assert errors[-1] < errors[0]

    learned_prediction = predictor.predict(
        hypothesis
    )

    assert abs(
        learned_prediction - 2.0
    ) < 0.01


def test_transfer_starts_with_prior_knowledge_not_zero():
    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    hypothesis = "effect_of_increase_temperature"

    predictor.set_prediction(
        hypothesis=hypothesis,
        prediction=1.0
    )

    environment_b = EnvironmentB()

    prediction_before_experience = predictor.predict(
        hypothesis
    )

    result = environment_b.step(
        "increase_temperature"
    )

    actual_effect = result["actual_effect"]

    assert prediction_before_experience == 1.0

    assert actual_effect == 2.0

    assert abs(
        actual_effect - prediction_before_experience
    ) == 1.0

    predictor.update(
        hypothesis=hypothesis,
        actual=actual_effect
    )

    prediction_after_experience = predictor.predict(
        hypothesis
    )

    # The expected mathematical update is 1.5,
    # but allow a small numerical/quantization tolerance.
    assert abs(
        prediction_after_experience - 1.5
    ) < 0.001
