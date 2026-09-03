from core.experiment import ExperimentManager
from core.hypothesis import HypothesisEngine
from core.simulation import SimulationEngine
from core.experiment_learning import ExperimentLearningEngine


def create_manager(max_experiments=10):
    return ExperimentManager(
        hypothesis_engine=HypothesisEngine(),
        simulation_engine=SimulationEngine(),
        max_experiments=max_experiments
    )


def test_experiment_manager_creates_learning_engine():

    manager = create_manager()

    assert isinstance(
        manager.learning_engine,
        ExperimentLearningEngine
    )


def test_evaluated_experiment_is_sent_to_learning():

    manager = create_manager(
        max_experiments=1
    )

    goal_state = {
        "goal": "reduce_prediction_error"
    }

    state = {
        "difference": 10
    }

    status = manager.start(
        goal_state,
        state
    )

    assert status["experiment_count"] == 1

    assert status["learning"]["record_count"] == 1

    assert len(
        status["learning"]["records"]
    ) == 1


def test_learning_record_contains_experiment_hypothesis():

    manager = create_manager(
        max_experiments=1
    )

    goal_state = {
        "goal": "reduce_prediction_error"
    }

    state = {
        "difference": 10
    }

    manager.start(
        goal_state,
        state
    )

    learning_status = manager.get_learning_status()

    assert learning_status["record_count"] == 1

    record = learning_status["records"][0]

    assert record["hypothesis"] == (
        "use_recent_experience"
    )

    assert record["predicted_difference"] == 5.0


def test_learning_status_exposes_best_hypothesis():

    manager = create_manager(
        max_experiments=3
    )

    goal_state = {
        "goal": "reduce_prediction_error"
    }

    state = {
        "difference": 10
    }

    manager.start(
        goal_state,
        state
    )

    learning_status = manager.get_learning_status()

    assert learning_status["best_hypothesis"] == (
        "use_recent_experience"
    )


def test_learning_status_exposes_hypothesis_performance():

    manager = create_manager(
        max_experiments=3
    )

    goal_state = {
        "goal": "reduce_prediction_error"
    }

    state = {
        "difference": 10
    }

    manager.start(
        goal_state,
        state
    )

    performance = (
        manager
        .get_learning_status()
        ["hypothesis_performance"]
    )

    assert performance == {
        "use_recent_experience": 5.0,
        "increase_observation_frequency": 8.0,
        "change_prediction_strategy": 7.0
    }


def test_learning_history_survives_new_experiment_run():

    manager = create_manager(
        max_experiments=3
    )

    goal_state = {
        "goal": "reduce_prediction_error"
    }

    state = {
        "difference": 10
    }

    manager.start(
        goal_state,
        state
    )

    first_learning_count = (
        manager
        .get_learning_status()
        ["record_count"]
    )

    manager.start(
        goal_state,
        state
    )

    second_learning_count = (
        manager
        .get_learning_status()
        ["record_count"]
    )

    assert first_learning_count == 3

    assert second_learning_count == 6


def test_manager_status_contains_learning_information():

    manager = create_manager(
        max_experiments=1
    )

    goal_state = {
        "goal": "reduce_prediction_error"
    }

    state = {
        "difference": 10
    }

    status = manager.start(
        goal_state,
        state
    )

    assert "learning" in status

    assert "records" in status["learning"]

    assert "record_count" in status["learning"]

    assert "best_hypothesis" in status["learning"]

    assert "hypothesis_performance" in status["learning"]


def test_learning_engine_can_be_injected():

    learning_engine = ExperimentLearningEngine(
        max_records=50
    )

    manager = ExperimentManager(
        hypothesis_engine=HypothesisEngine(),
        simulation_engine=SimulationEngine(),
        max_experiments=1,
        learning_engine=learning_engine
    )

    assert manager.learning_engine is (
        learning_engine
    )


def test_injected_learning_engine_receives_records():

    learning_engine = ExperimentLearningEngine(
        max_records=50
    )

    manager = ExperimentManager(
        hypothesis_engine=HypothesisEngine(),
        simulation_engine=SimulationEngine(),
        max_experiments=2,
        learning_engine=learning_engine
    )

    manager.start(
        {
            "goal": "reduce_prediction_error"
        },
        {
            "difference": 10
        }
    )

    assert learning_engine.size() == 2

    assert (
        learning_engine.best_hypothesis()
        == "use_recent_experience"
    )
