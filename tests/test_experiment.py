from core.hypothesis import HypothesisEngine
from core.simulation import SimulationEngine
from core.evaluation import EvaluationEngine
from core.experiment import ExperimentManager


class SlowSimulationEngine(SimulationEngine):

    def simulate(self, hypothesis, state=None):
        """
        Add a very small delay so the asynchronous
        stop test can reliably interrupt the loop.
        """

        import time

        time.sleep(0.01)

        return super().simulate(
            hypothesis,
            state
        )


def create_manager(max_experiments=10):

    hypothesis_engine = HypothesisEngine()
    simulation_engine = SimulationEngine()

    return ExperimentManager(
        hypothesis_engine,
        simulation_engine,
        max_experiments=max_experiments
    )


def create_slow_manager(max_experiments=100):

    hypothesis_engine = HypothesisEngine()
    simulation_engine = SlowSimulationEngine()

    return ExperimentManager(
        hypothesis_engine,
        simulation_engine,
        max_experiments=max_experiments
    )


def test_experiment_manager_runs_continuously():

    manager = create_manager(
        max_experiments=10
    )

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
    assert result["experiment_count"] == 10
    assert len(result["results"]) == 10


def test_experiment_manager_repeats_hypotheses():

    manager = create_manager(
        max_experiments=5
    )

    result = manager.start(
        {
            "goal": "reduce_prediction_error"
        },
        {
            "difference": 10
        }
    )

    assert result["experiment_count"] == 5

    hypotheses = [
        item["hypothesis"]
        for item in result["results"]
    ]

    assert hypotheses == [
        "use_recent_experience",
        "increase_observation_frequency",
        "change_prediction_strategy",
        "use_recent_experience",
        "increase_observation_frequency"
    ]


def test_experiment_manager_records_results():

    manager = create_manager(
        max_experiments=3
    )

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


def test_experiment_manager_evaluates_results():

    manager = create_manager(
        max_experiments=3
    )

    result = manager.start(
        {
            "goal": "reduce_prediction_error"
        },
        {
            "difference": 10
        }
    )

    assert len(result["evaluations"]) == 3

    first = result["evaluations"][0]

    assert first["status"] == "evaluated"
    assert first["hypothesis"] == "use_recent_experience"
    assert first["predicted_difference"] == 5
    assert first["score"] == -5


def test_experiment_result_contains_evaluation():

    manager = create_manager(
        max_experiments=1
    )

    result = manager.start(
        {
            "goal": "reduce_prediction_error"
        },
        {
            "difference": 10
        }
    )

    first = result["results"][0]

    assert "evaluation" in first
    assert first["evaluation"]["status"] == "evaluated"
    assert first["evaluation"]["score"] == -5


def test_experiment_manager_selects_best_result():

    manager = create_manager(
        max_experiments=3
    )

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


def test_experiment_manager_records_best_evaluation():

    manager = create_manager(
        max_experiments=3
    )

    result = manager.start(
        {
            "goal": "reduce_prediction_error"
        },
        {
            "difference": 10
        }
    )

    best = result["best_evaluation"]

    assert best is not None
    assert best["status"] == "evaluated"
    assert best["hypothesis"] == "use_recent_experience"
    assert best["predicted_difference"] == 5
    assert best["score"] == -5


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
    assert len(result["evaluations"]) == 2


def test_experiment_manager_stop():

    manager = create_manager()

    stop_result = manager.stop()

    assert stop_result["status"] == "stopped"
    assert manager.is_running() is False
    assert manager.stop_requested is True


def test_experiment_manager_async_stop():

    manager = create_slow_manager(
        max_experiments=100
    )

    worker = manager.start_async(
        {
            "goal": "reduce_prediction_error"
        },
        {
            "difference": 10
        }
    )

    assert manager.is_running() is True

    stop_result = manager.stop()

    assert stop_result["status"] == "stopped"
    assert stop_result["stop_requested"] is True

    finished = manager.wait(
        timeout=2
    )

    assert finished is True
    assert manager.is_running() is False
    assert manager.stop_requested is True

    assert worker.is_alive() is False

    assert manager.experiment_count < 100


def test_experiment_manager_async_start():

    manager = create_slow_manager(
        max_experiments=2
    )

    worker = manager.start_async(
        {
            "goal": "reduce_prediction_error"
        },
        {
            "difference": 10
        }
    )

    finished = manager.wait(
        timeout=2
    )

    assert finished is True
    assert worker.is_alive() is False

    assert manager.is_running() is False
    assert manager.experiment_count == 2


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
