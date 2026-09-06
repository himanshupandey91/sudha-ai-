"""
Tests for Sudha AI Adaptive Hypothesis Planning Engine.
"""

from core.hypothesis_planner import HypothesisPlanningEngine


def test_generate_hypotheses():
    engine = HypothesisPlanningEngine()

    result = engine.generate_hypotheses(
        {"goal": "reduce_prediction_error"}
    )

    assert result["status"] == "generated"
    assert result["count"] == 3
    assert result["hypotheses"][0]["hypothesis"] == "use_recent_experience"


def test_select_best_hypothesis_without_learning():
    engine = HypothesisPlanningEngine()

    result = engine.select_hypothesis(
        {"goal": "reduce_prediction_error"}
    )

    assert result["status"] == "selected"
    assert result["hypothesis"]["hypothesis"] == "use_recent_experience"
    assert result["hypothesis"]["priority"] == 3


def test_create_plan():
    engine = HypothesisPlanningEngine()

    result = engine.create_plan(
        {"goal": "reduce_prediction_error"}
    )

    assert result["status"] == "planned"
    assert result["plan"]["goal"] == "reduce_prediction_error"
    assert "observe_new_data" in result["plan"]["plan"]


def test_create_reasoning_plan():
    engine = HypothesisPlanningEngine()

    result = engine.create_reasoning_plan(
        {"goal": "reduce_prediction_error"}
    )

    assert result["status"] == "ready"
    assert result["goal"] == "reduce_prediction_error"
    assert len(result["hypotheses"]) == 3
    assert result["selected_hypothesis"]["hypothesis"] == "use_recent_experience"


def test_continue_observation_goal():
    engine = HypothesisPlanningEngine()

    result = engine.create_reasoning_plan(
        {"goal": "continue_observation"}
    )

    assert result["status"] == "ready"
    assert result["selected_hypothesis"]["hypothesis"] == "collect_more_observations"


def test_unknown_goal():
    engine = HypothesisPlanningEngine()

    result = engine.create_reasoning_plan(
        {"goal": "unknown_goal"}
    )

    assert result["status"] == "ready"
    assert result["selected_hypothesis"]["hypothesis"] == "collect_more_information"


def test_empty_goal():
    engine = HypothesisPlanningEngine()

    result = engine.create_reasoning_plan({})

    assert result["status"] == "unavailable"
    assert result["reason"] == "no_hypothesis_available"


def test_invalid_goal_state():
    engine = HypothesisPlanningEngine()

    result = engine.generate_hypotheses("invalid")

    assert result["status"] == "failed"
    assert result["reason"] == "hypothesis_generation_failed"


def test_configuration():
    engine = HypothesisPlanningEngine()

    configuration = engine.get_configuration()

    assert configuration["hypothesis_engine"] == "HypothesisEngine"
    assert configuration["planning_engine"] == "PlanningEngine"
    assert configuration["hypothesis_learning"] == "HypothesisLearningEngine"


def test_record_result():
    engine = HypothesisPlanningEngine()

    result = engine.record_result(
        "use_recent_experience",
        5
    )

    assert result["status"] == "recorded"
    assert result["hypothesis"] == "use_recent_experience"
    assert result["attempts"] == 1
    assert result["average_error"] == 5


def test_learned_hypothesis_can_override_static_priority():
    engine = HypothesisPlanningEngine()

    engine.record_result(
        "use_recent_experience",
        10
    )

    engine.record_result(
        "increase_observation_frequency",
        2
    )

    result = engine.select_hypothesis(
        {"goal": "reduce_prediction_error"}
    )

    assert result["status"] == "selected"

    assert (
        result["hypothesis"]["hypothesis"]
        == "increase_observation_frequency"
    )

    assert result["hypothesis"]["learned"] is True
    assert result["hypothesis"]["average_error"] == 2
    assert result["hypothesis"]["attempts"] == 1
    assert result["hypothesis"]["priority"] == 2

    assert abs(
        result["hypothesis"]["score"] - (1 / 3)
    ) < 1e-9


def test_learned_hypothesis_selection():
    engine = HypothesisPlanningEngine()

    engine.record_result(
        "use_recent_experience",
        8
    )

    engine.record_result(
        "increase_observation_frequency",
        2
    )

    result = engine.create_reasoning_plan(
        {"goal": "reduce_prediction_error"}
    )

    assert result["status"] == "ready"

    assert (
        result["selected_hypothesis"]["hypothesis"]
        == "increase_observation_frequency"
    )

    assert result["selected_hypothesis"]["learned"] is True


def test_reasoning_plan_uses_learning():
    engine = HypothesisPlanningEngine()

    engine.record_result(
        "change_prediction_strategy",
        1
    )

    result = engine.create_reasoning_plan(
        {"goal": "reduce_prediction_error"}
    )

    assert result["status"] == "ready"

    assert (
        result["selected_hypothesis"]["hypothesis"]
        == "change_prediction_strategy"
    )

    assert result["selected_hypothesis"]["learned"] is True


def test_get_learned_hypotheses():
    engine = HypothesisPlanningEngine()

    engine.record_result(
        "use_recent_experience",
        5
    )

    engine.record_result(
        "increase_observation_frequency",
        2
    )

    learned = engine.get_learned_hypotheses()

    assert len(learned) == 2
    assert (
        learned[0]["hypothesis"]
        == "increase_observation_frequency"
    )


def test_clear_learning():
    engine = HypothesisPlanningEngine()

    engine.record_result(
        "use_recent_experience",
        5
    )

    assert len(engine.get_learned_hypotheses()) == 1

    result = engine.clear_learning()

    assert result["status"] == "cleared"
    assert result["count"] == 0

    assert engine.get_learned_hypotheses() == []


def test_invalid_record_result():
    engine = HypothesisPlanningEngine()

    result = engine.record_result(
        "",
        5
    )

    assert result["status"] == "failed"
    assert result["reason"] == "hypothesis_result_recording_failed"
