"""
Tests for Sudha AI Experiment Manager.

Step 29-B

Focus:
- Experiment execution
- Hypothesis exploration
- Learning-based selection
- Best-result tracking
- Stop control
"""


from core.experiment import ExperimentManager
from core.hypothesis import HypothesisEngine
from core.simulation import SimulationEngine
from core.experiment_learning import (
    ExperimentLearningEngine
)


def create_manager(max_experiments=10):
    return ExperimentManager(
        hypothesis_engine=HypothesisEngine(),
        simulation_engine=SimulationEngine(),
        max_experiments=max_experiments
    )


def create_manager_with_learning(max_experiments=10):
    learning_engine = ExperimentLearningEngine()

    manager = ExperimentManager(
        hypothesis_engine=HypothesisEngine(),
        simulation_engine=SimulationEngine(),
        max_experiments=max_experiments,
        learning_engine=learning_engine
    )

    return manager


def test_manager_initializes():
    manager = create_manager()

    assert manager.running is False
    assert manager.experiment_count == 0
    assert manager.results == []
    assert manager.evaluations == []


def test_manager_requires_positive_max_experiments():
    try:
        ExperimentManager(
            hypothesis_engine=HypothesisEngine(),
            simulation_engine=SimulationEngine(),
            max_experiments=0
        )
        assert False
    except ValueError:
        assert True


def test_manager_rejects_invalid_max_experiments_type():
    try:
        ExperimentManager(
            hypothesis_engine=HypothesisEngine(),
            simulation_engine=SimulationEngine(),
            max_experiments="10"
        )
        assert False
    except TypeError:
        assert True


def test_manager_runs_experiment():
    manager = create_manager()

    goal_state = {
        "goal": "reduce_prediction_error"
    }

    state = {
        "difference": 10
    }

    result = manager.start(
        goal_state,
        state
    )

    assert result["experiment_count"] > 0
    assert len(result["results"]) > 0


def test_manager_explores_hypotheses_first():
    manager = create_manager(
        max_experiments=3
    )

    goal_state = {
        "goal": "reduce_prediction_error"
    }

    state = {
        "difference": 10
    }

    result = manager.start(
        goal_state,
        state
    )

    assert result["explored_hypotheses"] == [
        "use_recent_experience",
        "increase_observation_frequency",
        "change_prediction_strategy"
    ]


def test_manager_records_evaluations():
    manager = create_manager()

    goal_state = {
        "goal": "reduce_prediction_error"
    }

    state = {
        "difference": 10
    }

    result = manager.start(
        goal_state,
        state
    )

    assert len(result["evaluations"]) > 0

    for evaluation in result["evaluations"]:
        assert evaluation["status"] == "evaluated"


def test_manager_tracks_best_result():
    manager = create_manager(
        max_experiments=3
    )

    goal_state = {
        "goal": "reduce_prediction_error"
    }

    state = {
        "difference": 10
    }

    result = manager.start(
        goal_state,
        state
    )

    assert result["best_result"] is not None
    assert result["best_evaluation"] is not None

    assert (
        result["best_evaluation"]["predicted_difference"]
        == 5
    )


def test_manager_learns_from_evaluations():
    manager = create_manager()

    goal_state = {
        "goal": "reduce_prediction_error"
    }

    state = {
        "difference": 10
    }

    result = manager.start(
        goal_state,
        state
    )

    learning = result["learning"]

    assert learning["record_count"] > 0
    assert len(learning["records"]) > 0


def test_manager_learning_persists_between_runs():
    manager = create_manager()

    goal_state = {
        "goal": "reduce_prediction_error"
    }

    state = {
        "difference": 10
    }

    first_result = manager.start(
        goal_state,
        state
    )

    first_count = first_result[
        "learning"
    ]["record_count"]

    second_result = manager.start(
        goal_state,
        state
    )

    second_count = second_result[
        "learning"
    ]["record_count"]

    assert second_count > first_count


def test_manager_selects_learned_best_hypothesis():
    manager = create_manager_with_learning(
        max_experiments=5
    )

    manager.learning_engine.learn({
        "status": "evaluated",
        "hypothesis": "change_prediction_strategy",
        "predicted_difference": 1,
        "score": -1
    })

    hypotheses = manager.hypothesis_engine.generate({
        "goal": "reduce_prediction_error"
    })

    selected = manager._select_hypothesis(
        hypotheses
    )

    assert selected["hypothesis"] == (
        "change_prediction_strategy"
    )


def test_manager_explores_unseen_hypothesis_before_learning():
    manager = create_manager_with_learning(
        max_experiments=5
    )

    manager.learning_engine.learn({
        "status": "evaluated",
        "hypothesis": "use_recent_experience",
        "predicted_difference": 1,
        "score": -1
    })

    manager.explored_hypotheses = [
        "use_recent_experience"
    ]

    hypotheses = manager.hypothesis_engine.generate({
        "goal": "reduce_prediction_error"
    })

    selected = manager._select_hypothesis(
        hypotheses
    )

    assert selected["hypothesis"] == (
        "increase_observation_frequency"
    )


def test_manager_stop_before_start():
    manager = create_manager()

    result = manager.stop()

    assert result["status"] == "stopped"
    assert result["stop_requested"] is True
    assert manager.is_running() is False


def test_manager_status_contains_learning():
    manager = create_manager()

    status = manager.get_status()

    assert "learning" in status
    assert "records" in status["learning"]
    assert "best_hypothesis" in status["learning"]
    assert "hypothesis_performance" in status["learning"]


def test_manager_learning_status():
    manager = create_manager()

    status = manager.get_learning_status()

    assert status["records"] == []
    assert status["record_count"] == 0
    assert status["best_hypothesis"] is None
    assert status["hypothesis_performance"] == [] or (
        status["hypothesis_performance"] == {}
    )
