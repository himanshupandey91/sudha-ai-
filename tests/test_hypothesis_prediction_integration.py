"""
Sudha AI - Hypothesis Prediction Integration Tests

Step 60-A

Validates:

Selected Hypothesis
        ↓
CognitiveExperimentEngine
        ↓
ExperimentLoopEngine
        ↓
ClosedLoopLearningEngine
        ↓
PredictionEngine
        ↓
Hypothesis-specific Prediction
"""

from core.cognitive_experiment import CognitiveExperimentEngine
from core.experiment_loop import ExperimentLoopEngine
from core.closed_loop import ClosedLoopLearningEngine
from core.prediction import PredictionEngine


def test_prediction_changes_with_hypothesis():
    prediction_engine = PredictionEngine(
        hypothesis_predictions={
            "hypothesis_a": 5,
            "hypothesis_b": 15,
        }
    )

    closed_loop = ClosedLoopLearningEngine(
        prediction_engine=prediction_engine
    )

    experiment_loop = ExperimentLoopEngine(
        closed_loop=closed_loop
    )

    engine = CognitiveExperimentEngine(
        experiment_loop=experiment_loop
    )

    result_a = engine.predict(
        observation=10,
        hypothesis={
            "hypothesis": "hypothesis_a"
        }
    )

    result_b = engine.predict(
        observation=10,
        hypothesis={
            "hypothesis": "hypothesis_b"
        }
    )

    assert result_a["status"] == "predicted"
    assert result_b["status"] == "predicted"

    assert result_a["prediction"] == 5
    assert result_b["prediction"] == 15

    assert result_a["prediction"] != result_b["prediction"]


def test_selected_hypothesis_reaches_prediction_engine():
    prediction_engine = PredictionEngine(
        hypothesis_predictions={
            "selected_hypothesis": 42
        }
    )

    closed_loop = ClosedLoopLearningEngine(
        prediction_engine=prediction_engine
    )

    experiment_loop = ExperimentLoopEngine(
        closed_loop=closed_loop
    )

    engine = CognitiveExperimentEngine(
        experiment_loop=experiment_loop
    )

    hypothesis = {
        "hypothesis": "selected_hypothesis"
    }

    result = engine.predict(
        observation=10,
        hypothesis=hypothesis
    )

    assert result["status"] == "predicted"
    assert result["prediction"] == 42
    assert result["hypothesis"] == hypothesis


def test_legacy_prediction_still_works():
    engine = CognitiveExperimentEngine()

    result = engine.predict(
        observation=25
    )

    assert result["status"] == "predicted"
    assert result["prediction"] == 25


def test_unknown_hypothesis_falls_back_to_observation():
    prediction_engine = PredictionEngine(
        hypothesis_predictions={
            "known": 100
        }
    )

    closed_loop = ClosedLoopLearningEngine(
        prediction_engine=prediction_engine
    )

    experiment_loop = ExperimentLoopEngine(
        closed_loop=closed_loop
    )

    engine = CognitiveExperimentEngine(
        experiment_loop=experiment_loop
    )

    result = engine.predict(
        observation=25,
        hypothesis={
            "hypothesis": "unknown"
        }
    )

    assert result["status"] == "predicted"
    assert result["prediction"] == 25
