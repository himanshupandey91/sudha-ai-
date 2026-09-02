from core.hypothesis import HypothesisEngine
from core.simulation import SimulationEngine
from core.experiment import ExperimentManager


def create_manager(max_experiments=10):
    hypothesis_engine = HypothesisEngine()
    simulation_engine = SimulationEngine()

    return ExperimentManager(
        hypothesis_engine,
        simulation_engine,
        max_experiments=max_experiments
    )


def test_experiment_manager_starts_and_completes():

    manager = create_manager()

    result = manager.start(
        {
            "goal": "reduce_prediction_error",
            "priority": 5
        },
        {
            "difference": 10
        }
    )

    assert result["running"] is False
    assert result["experiment_count"] == 3
    assert len(result["results"]) == 3


def test_experiment_manager_records_results():

    manager = create_manager()

    result = manager.start(
        {
            "goal": "reduce_prediction_error"
        },
        {
            "difference": 10
        }
    )

    assert len(result["results"]) == 3

    first = result["results"][0]

    assert first["experiment"] == 1
    assert first["hypothesis"] == "use_recent_experience"
    assert first["result"]["status"] == "completed"


def test_experiment_manager_selects_best_result():

    manager = create_manager()

    result = manager.start(
        {
            "goal": "reduce_prediction_error"
        },
        {
            "difference": 10
        }
    )

    best = result["best_result"]

    assert best is not None
    assert best["hypothesis"] == "use_recent_experience"
    assert best["result"]["predicted_difference"] == 5


def test_experiment_manager_respects_max_experiments():

    manager = create_manager(
        max_experiments=2
    )

    result = manager.start(
        {
            "goal": "reduce_prediction_error"
        },
        {
            "difference": 10
        }
    )

    assert result["experiment_count"] == 2
    assert len(result["results"]) == 2


def test_experiment_manager_stop():

    manager = create_manager()

    stop_result = manager.stop()

    assert stop_result["status"] == "stopped"
    assert manager.is_running() is False


def test_experiment_manager_rejects_invalid_goal():

    manager = create_manager()

    try:
        manager.start(
            "invalid",
            {
                "difference": 10
            }
        )

        assert False

    except TypeError as error:
        assert str(error) == "goal_state must be a dictionary"


def test_experiment_manager_rejects_invalid_state():

    manager = create_manager()

    try:
        manager.start(
            {
                "goal": "reduce_prediction_error"
            },
            "invalid"
        )

        assert False

    except TypeError as error:
        assert str(error) == "state must be a dictionary"
