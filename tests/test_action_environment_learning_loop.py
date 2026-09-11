from core.action import ActionEngine
from core.adaptive_predictor import AdaptivePredictor
from core.environment import Environment


def test_action_selection_environment_execution_and_learning_loop():
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

    current_temperature = environment.get_state()["temperature"]

    goal_temperature = 22.0

    predicted_effects = {
        "increase_temperature": predictor.predict(
            "effect_of_increase_temperature"
        ),
        "decrease_temperature": predictor.predict(
            "effect_of_decrease_temperature"
        )
    }

    selection = action_engine.select_action(
        {
            "current_state": {
                "temperature": current_temperature
            },
            "goal": {
                "temperature": goal_temperature
            },
            "predicted_effects": predicted_effects,
            "available_actions": [
                "increase_temperature",
                "decrease_temperature"
            ]
        }
    )

    assert selection["status"] == "selected"
    assert selection["action"] == "increase_temperature"

    before_temperature = environment.get_state()["temperature"]

    result = environment.step(
        selection["action"]
    )

    actual_temperature = result["actual"]

    actual_effect = (
        actual_temperature - before_temperature
    )

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
