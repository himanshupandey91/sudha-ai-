from core.cognitive_experiment import (
    CognitiveExperimentEngine
)
from core.experiment_loop import ExperimentLoopEngine


class FakeExperiment:

    def __init__(self, result=15):
        self.result = result
        self.calls = []

    def run(self, observation):
        self.calls.append(observation)
        return self.result


def create_engine(result=15):
    experiment = FakeExperiment(result=result)

    experiment_loop = ExperimentLoopEngine(
        experiment=experiment
    )

    engine = CognitiveExperimentEngine(
        experiment_loop=experiment_loop
    )

    return engine, experiment


def test_reasoning_plan():
    engine = CognitiveExperimentEngine()

    result = engine.reason(
        {
            "goal": "reduce_prediction_error"
        }
    )

    assert result["status"] == "ready"
    assert result["goal"] == "reduce_prediction_error"
    assert len(result["hypotheses"]) == 3

    assert (
        result["selected_hypothesis"]["hypothesis"]
        == "use_recent_experience"
    )

    assert result["selected_hypothesis"]["priority"] == 3

    assert result["plan"]["goal"] == (
        "reduce_prediction_error"
    )


def test_continue_observation_reasoning():
    engine = CognitiveExperimentEngine()

    result = engine.reason(
        {
            "goal": "continue_observation"
        }
    )

    assert result["status"] == "ready"

    assert (
        result["selected_hypothesis"]["hypothesis"]
        == "collect_more_observations"
    )

    assert result["plan"]["plan"] == [
        "observe_new_data"
    ]


def test_unknown_goal_reasoning():
    engine = CognitiveExperimentEngine()

    result = engine.reason(
        {
            "goal": "unknown_goal"
        }
    )

    assert result["status"] == "ready"

    assert (
        result["selected_hypothesis"]["hypothesis"]
        == "collect_more_information"
    )

    assert result["plan"]["plan"] == [
        "observe_new_data"
    ]


def test_empty_goal_reasoning():
    engine = CognitiveExperimentEngine()

    result = engine.reason({})

    assert result["status"] == "unavailable"
    assert result["reason"] == (
        "no_hypothesis_available"
    )


def test_prediction():
    engine = CognitiveExperimentEngine()

    result = engine.predict(10)

    assert result["status"] == "predicted"
    assert result["prediction"] == 10


def test_run_cycle_without_experiment():
    engine = CognitiveExperimentEngine()

    result = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert result["status"] == "unavailable"
    assert result["goal"] == "reduce_prediction_error"
    assert result["observation"] == 10

    assert len(result["hypotheses"]) == 3

    assert (
        result["selected_hypothesis"]["hypothesis"]
        == "use_recent_experience"
    )

    assert result["plan"]["goal"] == (
        "reduce_prediction_error"
    )

    assert (
        result["experiment"]["reason"]
        == "experiment_not_configured"
    )


def test_run_cycle_unknown_goal_without_experiment():
    engine = CognitiveExperimentEngine()

    result = engine.run_cycle(
        {
            "goal": "unknown_goal"
        },
        20
    )

    assert result["status"] == "unavailable"
    assert result["goal"] == "unknown_goal"
    assert result["observation"] == 20

    assert (
        result["selected_hypothesis"]["hypothesis"]
        == "collect_more_information"
    )

    assert (
        result["experiment"]["reason"]
        == "experiment_not_configured"
    )


def test_full_cognitive_experiment_cycle():
    engine, experiment = create_engine(result=15)

    result = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert result["status"] == "completed"
    assert result["goal"] == "reduce_prediction_error"

    assert result["observation"] == 10
    assert result["prediction"] == 10
    assert result["actual"] == 15
    assert result["difference"] == 5

    assert result["learning"]["error"] == 5
    assert result["learning"]["learning_signal"] == 5

    assert isinstance(result["world_model"], dict)

    assert result["cycle"]["cycle"] == 1
    assert result["cycle"]["observation"] == 10
    assert result["cycle"]["prediction"] == 10
    assert result["cycle"]["actual"] == 15
    assert result["cycle"]["difference"] == 5

    assert result["stopped"] is False
    assert experiment.calls == [10]

    assert engine.get_cycle_count() == 1


def test_previous_experience_influences_next_cycle():
    engine, experiment = create_engine(result=15)

    first = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert first["status"] == "completed"
    assert first["prediction"] == 10
    assert first["actual"] == 15
    assert first["difference"] == 5

    experiment.result = 25

    second = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        20
    )

    assert second["status"] == "completed"
    assert second["prediction"] == 25
    assert second["actual"] == 25
    assert second["difference"] == 0

    assert engine.get_cycle_count() == 2
    assert experiment.calls == [10, 20]


def test_world_model_receives_experiment_result():
    engine, _ = create_engine(result=18)

    result = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert result["status"] == "completed"

    state = (
        engine.experiment_loop
        .closed_loop
        .experience_learning
        .get_world_state()
    )

    assert state["experience_count"] == 1


def test_experiment_history_is_preserved():
    engine, experiment = create_engine(result=15)

    first = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert first["status"] == "completed"

    experiment.result = 25

    second = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        20
    )

    assert second["status"] == "completed"

    history = engine.get_history()

    assert len(history) == 2

    assert history[0]["observation"] == 10
    assert history[0]["actual"] == 15

    assert history[1]["observation"] == 20
    assert history[1]["actual"] == 25


def test_stop():
    engine, _ = create_engine()

    result = engine.stop()

    assert result["status"] == "stopped"
    assert engine.is_stopped() is True


def test_reset():
    engine, _ = create_engine()

    first = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert first["status"] == "completed"
    assert engine.get_cycle_count() == 1

    result = engine.reset()

    assert result["status"] == "reset"
    assert engine.get_cycle_count() == 0
    assert engine.is_stopped() is False
    assert engine.get_history() == []


def test_invalid_goal_state():
    engine = CognitiveExperimentEngine()

    result = engine.reason("invalid")

    assert result["status"] == "failed"
    assert result["reason"] == (
        "hypothesis_generation_failed"
    )


def test_configuration():
    engine = CognitiveExperimentEngine()

    configuration = engine.get_configuration()

    assert configuration["hypothesis_planner"] == (
        "HypothesisPlanningEngine"
    )

    assert configuration["experiment_loop"] == (
        "ExperimentLoopEngine"
    )
