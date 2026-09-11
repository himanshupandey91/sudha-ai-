from core.action import ActionEngine
from core.action_learning_loop import ActionLearningLoop
from core.adaptive_predictor import AdaptivePredictor
from core.environment import Environment


def test_100_cycle_action_learning_reduces_prediction_error():
    environment = Environment()

    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    action_engine = ActionEngine()

    increase_hypothesis = (
        "effect_of_increase_temperature"
    )

    decrease_hypothesis = (
        "effect_of_decrease_temperature"
    )

    predictor.set_prediction(
        hypothesis=increase_hypothesis,
        prediction=0.0
    )

    predictor.set_prediction(
        hypothesis=decrease_hypothesis,
        prediction=-1.0
    )

    loop = ActionLearningLoop(
        predictor=predictor,
        action_engine=action_engine,
        environment=environment,
        action_hypotheses={
            "increase_temperature": increase_hypothesis,
            "decrease_temperature": decrease_hypothesis,
        },
        available_actions=[
            "increase_temperature",
            "decrease_temperature",
        ],
    )

    result = loop.run(
        goal_temperature=120.0,
        cycles=100,
    )

    assert result["status"] == "completed"
    assert result["cycles"] == 100

    assert result["initial_error"] > result["final_error"]

    assert result["final_error"] < 0.05

    learned_prediction = predictor.predict(
        increase_hypothesis
    )

    assert abs(
        1.0 - learned_prediction
    ) < 0.05

    assert len(
        result["history"]
    ) == 100


def test_learning_loop_uses_actual_environment_effect():
    environment = Environment()

    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    action_engine = ActionEngine()

    increase_hypothesis = (
        "effect_of_increase_temperature"
    )

    decrease_hypothesis = (
        "effect_of_decrease_temperature"
    )

    predictor.set_prediction(
        hypothesis=increase_hypothesis,
        prediction=0.0
    )

    predictor.set_prediction(
        hypothesis=decrease_hypothesis,
        prediction=-1.0
    )

    loop = ActionLearningLoop(
        predictor=predictor,
        action_engine=action_engine,
        environment=environment,
        action_hypotheses={
            "increase_temperature": increase_hypothesis,
            "decrease_temperature": decrease_hypothesis,
        },
        available_actions=[
            "increase_temperature",
            "decrease_temperature",
        ],
    )

    result = loop.run_cycle(
        goal_temperature=25.0
    )

    assert result["status"] == "completed"

    assert result["action"] == "increase_temperature"

    assert result["before_temperature"] == 20.0

    assert result["actual_temperature"] == 21.0

    assert result["actual_effect"] == 1.0

    assert result["predicted_effect"] == 0.0

    assert result["prediction_error"] == 1.0

    assert result["learned_prediction"] == 0.5
