"""
Tests for Sudha AI Executive Reasoning Engine.

Step 65-C

Tests:
- hypothesis validation
- evidence extraction
- lowest-error decision
- score-based decision
- unresolved hypotheses
- bounded exploration
- decision history
- configuration
"""

import pytest

from core.executive_reasoning import ExecutiveReasoningEngine


def test_engine_initializes():
    engine = ExecutiveReasoningEngine()

    assert engine.exploration is False
    assert engine.get_history() == []


def test_invalid_exploration_is_rejected():
    with pytest.raises(TypeError):
        ExecutiveReasoningEngine(exploration="yes")


def test_hypothesis_requires_dictionary():
    engine = ExecutiveReasoningEngine()

    with pytest.raises(TypeError):
        engine.evaluate_hypothesis("invalid")


def test_hypothesis_requires_name():
    engine = ExecutiveReasoningEngine()

    with pytest.raises(ValueError):
        engine.evaluate_hypothesis(
            {
                "average_error": 5
            }
        )


def test_empty_hypothesis_name_is_rejected():
    engine = ExecutiveReasoningEngine()

    with pytest.raises(ValueError):
        engine.evaluate_hypothesis(
            {
                "name": "   ",
                "average_error": 5
            }
        )


def test_lower_prediction_error_is_evaluated():
    engine = ExecutiveReasoningEngine()

    result = engine.evaluate_hypothesis(
        {
            "name": "hypothesis_a",
            "average_error": 4
        }
    )

    assert result == {
        "name": "hypothesis_a",
        "status": "evaluated",
        "criterion": "prediction_error",
        "error": 4.0,
        "score": None,
    }


def test_explicit_score_can_be_used_when_error_is_missing():
    engine = ExecutiveReasoningEngine()

    result = engine.evaluate_hypothesis(
        {
            "name": "hypothesis_a",
            "score": 8
        }
    )

    assert result == {
        "name": "hypothesis_a",
        "status": "evaluated",
        "criterion": "score",
        "error": None,
        "score": 8.0,
    }


def test_missing_evidence_remains_unresolved():
    engine = ExecutiveReasoningEngine()

    result = engine.evaluate_hypothesis(
        {
            "name": "hypothesis_a"
        }
    )

    assert result == {
        "name": "hypothesis_a",
        "status": "unresolved",
        "criterion": None,
        "error": None,
        "score": None,
    }


def test_engine_selects_lowest_prediction_error():
    engine = ExecutiveReasoningEngine()

    result = engine.reason(
        [
            {
                "name": "hypothesis_a",
                "average_error": 10,
            },
            {
                "name": "hypothesis_b",
                "average_error": 3,
            },
            {
                "name": "hypothesis_c",
                "average_error": 7,
            },
        ]
    )

    assert result["status"] == "decision_selected"
    assert result["decision"]["selected"] == "hypothesis_b"
    assert result["decision"]["criterion"] == "prediction_error"
    assert result["decision"]["error"] == 3.0


def test_error_is_prioritized_over_score():
    engine = ExecutiveReasoningEngine()

    result = engine.reason(
        [
            {
                "name": "high_score",
                "score": 100,
            },
            {
                "name": "low_error",
                "average_error": 2,
            },
        ]
    )

    assert result["decision"]["selected"] == "low_error"
    assert result["decision"]["criterion"] == "prediction_error"


def test_highest_score_is_selected_when_no_error_exists():
    engine = ExecutiveReasoningEngine()

    result = engine.reason(
        [
            {
                "name": "hypothesis_a",
                "score": 2,
            },
            {
                "name": "hypothesis_b",
                "score": 9,
            },
            {
                "name": "hypothesis_c",
                "score": 5,
            },
        ]
    )

    assert result["decision"]["selected"] == "hypothesis_b"
    assert result["decision"]["criterion"] == "score"
    assert result["decision"]["score"] == 9.0


def test_no_decision_when_all_evidence_is_missing():
    engine = ExecutiveReasoningEngine()

    result = engine.reason(
        [
            {
                "name": "hypothesis_a",
            },
            {
                "name": "hypothesis_b",
            },
        ]
    )

    assert result["status"] == "no_decision"
    assert result["decision"]["selected"] is None
    assert result["decision"]["reason"] == "insufficient_evidence"


def test_exploration_selects_first_unresolved_hypothesis():
    engine = ExecutiveReasoningEngine(exploration=True)

    result = engine.reason(
        [
            {
                "name": "hypothesis_a",
            },
            {
                "name": "hypothesis_b",
            },
        ]
    )

    assert result["status"] == "decision_selected"
    assert result["decision"]["selected"] == "hypothesis_a"
    assert result["decision"]["criterion"] == "exploration"


def test_exploration_does_not_override_available_error():
    engine = ExecutiveReasoningEngine(exploration=True)

    result = engine.reason(
        [
            {
                "name": "unresolved",
            },
            {
                "name": "known",
                "average_error": 1,
            },
        ]
    )

    assert result["decision"]["selected"] == "known"
    assert result["decision"]["criterion"] == "prediction_error"


def test_history_records_selected_decisions():
    engine = ExecutiveReasoningEngine()

    engine.reason(
        [
            {
                "name": "hypothesis_a",
                "average_error": 5,
            },
            {
                "name": "hypothesis_b",
                "average_error": 2,
            },
        ]
    )

    history = engine.get_history()

    assert len(history) == 1
    assert history[0]["selected"] == "hypothesis_b"


def test_history_is_returned_as_copy():
    engine = ExecutiveReasoningEngine()

    engine.reason(
        [
            {
                "name": "hypothesis_a",
                "average_error": 2,
            }
        ]
    )

    history = engine.get_history()
    history.clear()

    assert len(engine.get_history()) == 1


def test_clear_history():
    engine = ExecutiveReasoningEngine()

    engine.reason(
        [
            {
                "name": "hypothesis_a",
                "average_error": 2,
            }
        ]
    )

    result = engine.clear_history()

    assert result["status"] == "cleared"
    assert engine.get_history() == []


def test_configuration_reports_engine_state():
    engine = ExecutiveReasoningEngine(exploration=True)

    configuration = engine.get_configuration()

    assert configuration["engine"] == "ExecutiveReasoningEngine"
    assert configuration["exploration"] is True
    assert configuration["history_size"] == 0


def test_empty_hypothesis_list_is_rejected():
    engine = ExecutiveReasoningEngine()

    with pytest.raises(ValueError):
        engine.evaluate([])


def test_invalid_hypothesis_collection_is_rejected():
    engine = ExecutiveReasoningEngine()

    with pytest.raises(TypeError):
        engine.evaluate("invalid")
