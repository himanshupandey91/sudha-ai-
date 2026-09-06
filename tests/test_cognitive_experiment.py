from core.cognitive_experiment import (
    CognitiveExperimentEngine
)


def test_reasoning_plan():
    engine = CognitiveExperimentEngine()

    result = engine.reason(
        {
            "goal": "reduce_prediction_error"
        }
    )

    assert result["status"] == "ready"
    assert result["goal"] == "reduce_prediction_error"

    assert len(result["hypotheses"]) == 3

    assert (
        result["selected_hypothesis"]["hypothesis"]
        == "use_recent_experience"
    )

    assert (
        result["selected_hypothesis"]["priority"]
        == 3
    )

    assert result["plan"]["goal"] == (
        "reduce_prediction_error"
    )


def test_continue_observation_reasoning():
    engine = CognitiveExperimentEngine()

    result = engine.reason(
        {
            "goal": "continue_observation"
        }
    )

    assert result["status"] == "ready"

    assert (
        result["selected_hypothesis"]["hypothesis"]
        == "collect_more_observations"
    )

    assert result["plan"]["plan"] == [
        "observe_new_data"
    ]


def test_unknown_goal_reasoning():
    engine = CognitiveExperimentEngine()

    result = engine.reason(
        {
            "goal": "unknown_goal"
        }
    )

    assert result["status"] == "ready"

    assert (
        result["selected_hypothesis"]["hypothesis"]
        == "collect_more_information"
    )

    assert result["plan"]["plan"] == [
        "observe_new_data"
    ]


def test_empty_goal_reasoning():
    engine = CognitiveExperimentEngine()

    result = engine.reason({})

    assert result["status"] == "unavailable"
    assert result["reason"] == (
        "no_hypothesis_available"
    )


def test_prediction():
    engine = CognitiveExperimentEngine()

    result = engine.predict(10)

    assert result["status"] == "predicted"
    assert result["prediction"] == 10


def test_run_cycle():
    engine = CognitiveExperimentEngine()

    result = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert result["status"] == "ready"
    assert result["goal"] == "reduce_prediction_error"

    assert result["observation"] == 10
    assert result["prediction"] == 10

    assert len(result["hypotheses"]) == 3

    assert (
        result["selected_hypothesis"]["hypothesis"]
        == "use_recent_experience"
    )

    assert result["plan"]["goal"] == (
        "reduce_prediction_error"
    )


def test_run_cycle_unknown_goal():
    engine = CognitiveExperimentEngine()

    result = engine.run_cycle(
        {
            "goal": "unknown_goal"
        },
        20
    )

    assert result["status"] == "ready"
    assert result["goal"] == "unknown_goal"
    assert result["observation"] == 20
    assert result["prediction"] == 20

    assert (
        result["selected_hypothesis"]["hypothesis"]
        == "collect_more_information"
    )


def test_invalid_goal_state():
    engine = CognitiveExperimentEngine()

    result = engine.reason("invalid")

    assert result["status"] == "failed"
    assert result["reason"] == (
        "hypothesis_generation_failed"
    )


def test_configuration():
    engine = CognitiveExperimentEngine()

    configuration = engine.get_configuration()

    assert configuration["hypothesis_planner"] == (
        "HypothesisPlanningEngine"
    )

    assert configuration["experiment_loop"] == (
        "ExperimentLoopEngine"
    )
