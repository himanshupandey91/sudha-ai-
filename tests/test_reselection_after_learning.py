from core.action import ActionEngine
from core.adaptive_predictor import AdaptivePredictor
from core.environment import Environment


def test_action_is_reselected_using_learned_effect():
    environment = Environment()
    action_engine = ActionEngine()

    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    predictor.set_prediction(
        hypothesis="effect_of_increase_temperature",
        prediction=0.0
    )

    predictor.set_prediction(
        hypothesis="effect_of_decrease_temperature",
        prediction=0.0
    )

    # First decision
    current_temperature = environment.get_state()["temperature"]

    predicted_effects = {
        "increase_temperature": predictor.predict(
            "effect_of_increase_temperature"
        ),
        "decrease_temperature": predictor.predict(
            "effect_of_decrease_temperature"
        )
    }

    first_selection = action_engine.select_action(
        {
            "current_state": {
                "temperature": current_temperature
            },
            "goal": {
                "temperature": 22.0
            },
            "predicted_effects": predicted_effects,
            "available_actions": [
                "increase_temperature",
                "decrease_temperature"
            ]
        }
    )

    assert first_selection["status"] == "selected"
    assert first_selection["action"] == "increase_temperature"

    # Execute selected action in the real environment
    before_temperature = environment.get_state()["temperature"]

    first_result = environment.step(
        first_selection["action"]
    )

    actual_temperature = first_result["actual"]

    actual_effect = (
        actual_temperature - before_temperature
    )

    # Learn from the actual result
    predictor.update(
        hypothesis="effect_of_increase_temperature",
        actual=actual_effect
    )

    learned_effect = predictor.predict(
        "effect_of_increase_temperature"
    )

    assert actual_temperature == 21.0
    assert actual_effect == 1.0
    assert learned_effect == 0.5

    # Second decision must use the learned prediction
    new_current_temperature = environment.get_state()["temperature"]

    new_predicted_effects = {
        "increase_temperature": predictor.predict(
            "effect_of_increase_temperature"
        ),
        "decrease_temperature": predictor.predict(
            "effect_of_decrease_temperature"
        )
    }

    second_selection = action_engine.select_action(
        {
            "current_state": {
                "temperature": new_current_temperature
            },
            "goal": {
                "temperature": 22.0
            },
            "predicted_effects": new_predicted_effects,
            "available_actions": [
                "increase_temperature",
                "decrease_temperature"
            ]
        }
    )

    assert second_selection["status"] == "selected"
    assert second_selection["action"] == "increase_temperature"
    assert second_selection["predicted_effect"] == 0.5
