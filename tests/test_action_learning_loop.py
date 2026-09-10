from core.adaptive_predictor import AdaptivePredictor
from core.environment import Environment


def test_action_environment_learning_loop():
    environment = Environment()

    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    hypothesis = "temperature_after_increase"

    predictor.set_prediction(
        hypothesis=hypothesis,
        prediction=20.0
    )

    prediction = predictor.predict(hypothesis)

    result = environment.step("increase_temperature")

    actual = result["actual"]

    error_before_learning = abs(actual - prediction)

    predictor.update(
        hypothesis=hypothesis,
        actual=actual
    )

    learned_prediction = predictor.predict(hypothesis)

    result = environment.step("increase_temperature")

    actual_next = result["actual"]

    error_after_learning = abs(
        actual_next - learned_prediction
    )

    assert actual == 21.0
    assert actual_next == 22.0

    assert error_after_learning < error_before_learning
