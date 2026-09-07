"""
Sudha AI - Hypothesis Learning Integration Tests

Step 60-B

Validates the complete controlled learning path:

Hypothesis
    ↓
Hypothesis-specific Prediction
    ↓
Experiment
    ↓
Actual Result
    ↓
Prediction Error
    ↓
Hypothesis Learning
    ↓
Better Hypothesis
    ↓
Next Selection
"""

from core.cognitive_experiment import CognitiveExperimentEngine
from core.experiment_loop import ExperimentLoopEngine
from core.closed_loop import ClosedLoopLearningEngine
from core.prediction import PredictionEngine
from core.hypothesis_planner import HypothesisPlanningEngine
from core.hypothesis_experiment import HypothesisExperiment


def test_hypothesis_performance_is_learned_from_cycle():
    prediction_engine = PredictionEngine(
        hypothesis_predictions={
            "use_recent_experience": 10,
            "explore_new_pattern": 5,
            "use_world_model": 3,
        }
    )

    closed_loop = ClosedLoopLearningEngine(
        prediction_engine=prediction_engine
    )

    experiment = HypothesisExperiment(
        outcomes={
            "use_recent_experience": 20,
            "explore_new_pattern": 7,
            "use_world_model": 30,
        }
    )

    experiment_loop = ExperimentLoopEngine(
        closed_loop=closed_loop,
        experiment=experiment
    )

    hypothesis_planner = HypothesisPlanningEngine()

    engine = CognitiveExperimentEngine(
        hypothesis_planner=hypothesis_planner,
        experiment_loop=experiment_loop
    )

    result = engine.run_cycle(
        goal_state={
            "goal": "reduce_prediction_error"
        },
        observation=10
    )

    assert result["status"] == "completed"

    selected = result["selected_hypothesis"]

    hypothesis_name = selected["hypothesis"]

    assert hypothesis_name == "use_recent_experience"

    assert result["prediction"] == 10

    assert result["actual"] == 20

    assert result["difference"] == 10

    learned = engine.get_learned_hypotheses()

    assert len(learned) == 1

    assert learned[0]["hypothesis"] == "use_recent_experience"

    assert learned[0]["average_error"] == 10


def test_lower_error_hypothesis_becomes_preferred():
    prediction_engine = PredictionEngine(
        hypothesis_predictions={
            "use_recent_experience": 10,
            "explore_new_pattern": 6,
            "use_world_model": 3,
        }
    )

    closed_loop = ClosedLoopLearningEngine(
        prediction_engine=prediction_engine
    )

    experiment = HypothesisExperiment(
        outcomes={
            "use_recent_experience": 20,
            "explore_new_pattern": 7,
            "use_world_model": 30,
        }
    )

    experiment_loop = ExperimentLoopEngine(
        closed_loop=closed_loop,
        experiment=experiment
    )

    hypothesis_planner = HypothesisPlanningEngine()

    engine = CognitiveExperimentEngine(
        hypothesis_planner=hypothesis_planner,
        experiment_loop=experiment_loop
    )

    first = engine.run_cycle(
        goal_state={
            "goal": "reduce_prediction_error"
        },
        observation=10
    )

    assert first["status"] == "completed"

    assert (
        first["selected_hypothesis"]["hypothesis"]
        == "use_recent_experience"
    )

    engine.hypothesis_planner.record_result(
        "explore_new_pattern",
        1
    )

    next_reasoning = engine.reason(
        {
            "goal": "reduce_prediction_error"
        }
    )

    assert next_reasoning["status"] == "ready"

    assert (
        next_reasoning["selected_hypothesis"]["hypothesis"]
        == "explore_new_pattern"
    )

    assert (
        next_reasoning["selected_hypothesis"]["average_error"]
        == 1
    )
