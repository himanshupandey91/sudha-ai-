from core.experiment_loop import ExperimentLoopEngine


class FakeExperiment:

    def __init__(self, result):
        self.result = result
        self.calls = []

    def run(self, observation):
        self.calls.append(observation)
        return self.result


def test_experiment_produces_actual_result():
    experiment = FakeExperiment(result=15)

    engine = ExperimentLoopEngine(
        experiment=experiment
    )

    result = engine.run_experiment(10)

    assert result["status"] == "experiment_completed"
    assert result["observation"] == 10
    assert result["actual"] == 15

    assert experiment.calls == [10]


def test_experiment_result_enters_learning_loop():
    experiment = FakeExperiment(result=15)

    engine = ExperimentLoopEngine(
        experiment=experiment
    )

    result = engine.run_cycle(10)

    assert result["status"] == "completed"

    assert result["observation"] == 10
    assert result["prediction"] == 10
    assert result["actual"] == 15
    assert result["difference"] == 5

    assert result["learning"]["error"] == 5

    assert result["world_model"]["observation"] == 10
    assert result["world_model"]["actual"] == 15

    assert engine.get_cycle_count() == 1


def test_previous_experience_changes_next_prediction():
    experiment = FakeExperiment(result=15)

    engine = ExperimentLoopEngine(
        experiment=experiment
    )

    first = engine.run_cycle(10)

    assert first["prediction"] == 10
    assert first["actual"] == 15
    assert first["difference"] == 5

    experiment.result = 25

    second = engine.run_cycle(20)

    assert second["prediction"] == 15
    assert second["actual"] == 25
    assert second["difference"] == 10

    assert engine.get_cycle_count() == 2


def test_experiment_error_is_not_learned():
    class FailingExperiment:

        def run(self, observation):
            raise RuntimeError("experiment failed")

    engine = ExperimentLoopEngine(
        experiment=FailingExperiment()
    )

    result = engine.run_cycle(10)

    assert result["status"] == "failed"
    assert result["reason"] == "experiment_execution_failed"

    assert engine.get_cycle_count() == 0


def test_missing_experiment_is_rejected():
    engine = ExperimentLoopEngine()

    result = engine.run_cycle(10)

    assert result["status"] == "unavailable"
    assert result["reason"] == "experiment_not_configured"

    assert engine.get_cycle_count() == 0


def test_manual_stop_prevents_experiment():
    experiment = FakeExperiment(result=15)

    engine = ExperimentLoopEngine(
        experiment=experiment
    )

    stop_result = engine.stop()

    assert stop_result["status"] == "stopped"

    result = engine.run_cycle(10)

    assert result["status"] == "stopped"
    assert result["reason"] == "closed_loop_stopped"

    assert experiment.calls == []


def test_max_cycles_stop_experiment_loop():
    experiment = FakeExperiment(result=15)

    engine = ExperimentLoopEngine(
        experiment=experiment,
        max_cycles=2
    )

    first = engine.run_cycle(10)
    second = engine.run_cycle(20)
    third = engine.run_cycle(30)

    assert first["status"] == "completed"
    assert second["status"] == "completed"

    assert second["stopped"] is True

    assert third["status"] == "stopped"
    assert third["reason"] == "closed_loop_stopped"

    assert len(experiment.calls) == 2
