"""
Sudha AI - Adaptive Hypothesis Planning Tests

Tests Version 0.2 behavior:
- Hypothesis generation
- Static selection
- Adaptive selection
- Learned hypothesis ranking
- Planning
- Reasoning plan
- Learning management
"""

import pytest

from core.hypothesis_planner import HypothesisPlanningEngine


def test_generate_hypotheses():
    engine = HypothesisPlanningEngine()

    result = engine.generate_hypotheses(
        {"goal": "reduce_prediction_error"}
    )

    assert result["status"] == "generated"
    assert result["count"] == 3
    assert result["hypotheses"][0]["hypothesis"] == (
        "use_recent_experience"
    )


def test_select_best_hypothesis_without_learning():
    engine = HypothesisPlanningEngine()

    result = engine.select_hypothesis(
        {"goal": "reduce_prediction_error"}
    )

    assert result["status"] == "selected"
    assert result["hypothesis"]["hypothesis"] == (
        "use_recent_experience"
    )
    assert result["hypothesis"]["priority"] == 3


def test_create_plan():
    engine = HypothesisPlanningEngine()

    result = engine.create_plan(
        {"goal": "reduce_prediction_error"}
    )

    assert result["status"] == "planned"
    assert result["plan"]["goal"] == (
        "reduce_prediction_error"
    )
    assert result["plan"]["plan"] == [
        "observe_new_data",
        "make_new_prediction",
        "compare_prediction_with_actual"
    ]


def test_create_reasoning_plan():
    engine = HypothesisPlanningEngine()

    result = engine.create_reasoning_plan(
        {"goal": "reduce_prediction_error"}
    )

    assert result["status"] == "ready"
    assert result["goal"] == (
        "reduce_prediction_error"
    )
    assert len(result["hypotheses"]) == 3
    assert result["selected_hypothesis"]["hypothesis"] == (
        "use_recent_experience"
    )
    assert result["plan"]["goal"] == (
        "reduce_prediction_error"
    )


def test_continue_observation_goal():
    engine = HypothesisPlanningEngine()

    result = engine.create_reasoning_plan(
        {"goal": "continue_observation"}
    )

    assert result["status"] == "ready"
    assert result["selected_hypothesis"]["hypothesis"] == (
        "collect_more_observations"
    )
    assert result["plan"]["plan"] == [
        "observe_new_data"
    ]


def test_unknown_goal():
    engine = HypothesisPlanningEngine()

    result = engine.create_reasoning_plan(
        {"goal": "unknown_goal"}
    )

    assert result["status"] == "ready"
    assert result["selected_hypothesis"]["hypothesis"] == (
        "collect_more_information"
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

    result = engine.get_configuration()

    assert result["hypothesis_engine"] == (
        "HypothesisEngine"
    )
    assert result["planning_engine"] == (
        "PlanningEngine"
    )
    assert result["hypothesis_learning"] == (
        "HypothesisLearningEngine"
    )


def test_record_result():
    engine = HypothesisPlanningEngine()

    result = engine.record_result(
        "use_recent_experience",
        5
    )

    assert result["status"] == "recorded"
    assert result["hypothesis"] == (
        "use_recent_experience"
    )
    assert result["attempts"] == 1
    assert result["average_error"] == 5
    assert result["score"] == pytest.approx(
        1 / 6
    )


def test_learned_hypothesis_can_override_static_priority():
    engine = HypothesisPlanningEngine()

    engine.record_result(
        "use_recent_experience",
        8
    )

    engine.record_result(
        "increase_observation_frequency",
        2
    )

    result = engine.select_hypothesis(
        {"goal": "reduce_prediction_error"}
    )

    assert result["status"] == "selected"

    selected = result["hypothesis"]

    assert selected["hypothesis"] == (
        "increase_observation_frequency"
    )

    assert selected["priority"] == 2
    assert selected["learned"] is True
    assert selected["attempts"] == 1
    assert selected["average_error"] == 2
    assert selected["score"] == pytest.approx(
        1 / 3
    )


def test_learned_hypothesis_selection():
    engine = HypothesisPlanningEngine()

    engine.record_result(
        "use_recent_experience",
        10
    )

    engine.record_result(
        "increase_observation_frequency",
        1
    )

    result = engine.create_reasoning_plan(
        {"goal": "reduce_prediction_error"}
    )

    assert result["status"] == "ready"

    selected = result["selected_hypothesis"]

    assert selected["hypothesis"] == (
        "increase_observation_frequency"
    )

    assert selected["learned"] is True
    assert selected["attempts"] == 1
    assert selected["average_error"] == 1
    assert selected["score"] == pytest.approx(
        1 / 2
    )


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

    result = engine.get_learned_hypotheses()

    assert len(result) == 2
    assert result[0]["hypothesis"] == (
        "increase_observation_frequency"
    )
    assert result[0]["average_error"] == 2
    assert result[1]["hypothesis"] == (
        "use_recent_experience"
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
        123,
        5
    )

    assert result["status"] == "failed"
    assert result["reason"] == (
        "hypothesis_result_recording_failed"
    )
