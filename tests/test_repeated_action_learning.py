from core.action import ActionEngine
from core.adaptive_predictor import AdaptivePredictor
from core.environment import Environment


def test_repeated_action_learning_converges():
    environment = Environment()
    action_engine = ActionEngine()

    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    increase_hypothesis = "effect_of_increase_temperature"
    decrease_hypothesis = "effect_of_decrease_temperature"

    predictor.set_prediction(
        hypothesis=increase_hypothesis,
        prediction=0.0
    )

    predictor.set_prediction(
        hypothesis=decrease_hypothesis,
        prediction=-1.0
    )

    learned_effects = []
    errors = []

    for _ in range(5):

        current_temperature = environment.get_state()["temperature"]

        predicted_effects = {
            "increase_temperature": predictor.predict(
                increase_hypothesis
            ),
            "decrease_temperature": predictor.predict(
                decrease_hypothesis
            )
        }

        selection = action_engine.select_action(
            {
                "current_state": {
                    "temperature": current_temperature
                },
                "goal": {
                    "temperature": 25.0
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

        prediction_before_learning = predictor.predict(
            increase_hypothesis
        )

        error = abs(
            actual_effect - prediction_before_learning
        )

        errors.append(error)

        predictor.update(
            hypothesis=increase_hypothesis,
            actual=actual_effect
        )

        learned_effect = predictor.predict(
            increase_hypothesis
        )

        learned_effects.append(learned_effect)

    assert learned_effects == [
        0.5,
        0.75,
        0.875,
        0.9375,
        0.96875
    ]

    assert errors[0] > errors[-1]

    assert all(
        errors[index + 1] < errors[index]
        for index in range(len(errors) - 1)
    )

    assert learned_effects[-1] < 1.0
    assert abs(1.0 - learned_effects[-1]) < 0.05
