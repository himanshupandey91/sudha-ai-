from core.adaptive_predictor import AdaptivePredictor
from core.environment import Environment


def test_action_effect_is_learned_from_actual_results():
    environment = Environment()

    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    hypothesis = "effect_of_increase_temperature"

    predictor.set_prediction(
        hypothesis=hypothesis,
        prediction=0.0
    )

    first_temperature = environment.get_state()["temperature"]

    result = environment.step("increase_temperature")

    actual_first = result["actual"]
    actual_effect = actual_first - first_temperature

    prediction_before = predictor.predict(hypothesis)

    error_before_learning = abs(
        actual_effect - prediction_before
    )

    predictor.update(
        hypothesis=hypothesis,
        actual=actual_effect
    )

    learned_effect = predictor.predict(hypothesis)

    second_temperature = environment.get_state()["temperature"]

    result = environment.step("increase_temperature")

    actual_second = result["actual"]
    actual_effect_next = actual_second - second_temperature

    error_after_learning = abs(
        actual_effect_next - learned_effect
    )

    assert actual_first == 21.0
    assert actual_effect == 1.0

    assert actual_second == 22.0
    assert actual_effect_next == 1.0

    assert error_after_learning < error_before_learning
