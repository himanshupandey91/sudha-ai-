from core.hypothesis_planner import (
    HypothesisPlanningEngine
)


def test_generate_hypotheses():
    engine = HypothesisPlanningEngine()

    result = engine.generate_hypotheses(
        {
            "goal": "reduce_prediction_error"
        }
    )

    assert result["status"] == "generated"
    assert result["count"] == 3
    assert len(result["hypotheses"]) == 3


def test_select_best_hypothesis():
    engine = HypothesisPlanningEngine()

    result = engine.select_hypothesis(
        {
            "goal": "reduce_prediction_error"
        }
    )

    assert result["status"] == "selected"
    assert result["hypothesis"]["hypothesis"] == (
        "use_recent_experience"
    )
    assert result["hypothesis"]["priority"] == 3


def test_create_plan():
    engine = HypothesisPlanningEngine()

    result = engine.create_plan(
        {
            "goal": "reduce_prediction_error"
        }
    )

    assert result["status"] == "planned"

    plan = result["plan"]

    assert plan["goal"] == "reduce_prediction_error"
    assert "observe_new_data" in plan["plan"]
    assert "make_new_prediction" in plan["plan"]
    assert "compare_prediction_with_actual" in plan["plan"]


def test_create_reasoning_plan():
    engine = HypothesisPlanningEngine()

    result = engine.create_reasoning_plan(
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


def test_continue_observation_goal():
    engine = HypothesisPlanningEngine()

    result = engine.create_reasoning_plan(
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


def test_unknown_goal():
    engine = HypothesisPlanningEngine()

    result = engine.create_reasoning_plan(
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


def test_empty_goal():
    engine = HypothesisPlanningEngine()

    result = engine.create_reasoning_plan({})

    assert result["status"] == "unavailable"
    assert result["reason"] == "no_hypothesis_available"


def test_invalid_goal_state():
    engine = HypothesisPlanningEngine()

    result = engine.generate_hypotheses(
        "invalid"
    )

    assert result["status"] == "failed"
    assert result["reason"] == (
        "hypothesis_generation_failed"
    )


def test_configuration():
    engine = HypothesisPlanningEngine()

    configuration = engine.get_configuration()

    assert configuration["hypothesis_engine"] == (
        "HypothesisEngine"
    )

    assert configuration["planning_engine"] == (
        "PlanningEngine"
    )
