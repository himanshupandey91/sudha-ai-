from core.cognitive_experiment import CognitiveExperimentEngine


class FakeExperiment:

    def __init__(self, result=15):
        self.result = result

    def run(self, observation):
        return self.result


class HypothesisAwareExperiment:

    def __init__(self, result=15):
        self.result = result
        self.received_hypothesis = None
        self.received_observation = None

    def run(self, observation, hypothesis=None):
        self.received_observation = observation
        self.received_hypothesis = hypothesis
        return self.result


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
    assert result["selected_hypothesis"]["hypothesis"] == (
        "use_recent_experience"
    )
    assert result["plan"]["goal"] == "reduce_prediction_error"


def test_reasoning_continue_observation():
    engine = CognitiveExperimentEngine()

    result = engine.reason(
        {
            "goal": "continue_observation"
        }
    )

    assert result["status"] == "ready"
    assert result["selected_hypothesis"]["hypothesis"] == (
        "collect_more_observations"
    )


def test_reasoning_unknown_goal():
    engine = CognitiveExperimentEngine()

    result = engine.reason(
        {
            "goal": "unknown_goal"
        }
    )

    assert result["status"] == "ready"
    assert result["selected_hypothesis"]["hypothesis"] == (
        "collect_more_information"
    )


def test_reasoning_empty_goal():
    engine = CognitiveExperimentEngine()

    result = engine.reason({})

    assert result["status"] == "unavailable"
    assert result["reason"] == "no_hypothesis_available"


def test_predict():
    experiment = FakeExperiment()

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

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
    assert result["reason"] == "experiment_not_configured"


def test_run_cycle_unknown_goal_without_experiment():
    engine = CognitiveExperimentEngine()

    result = engine.run_cycle(
        {
            "goal": "unknown_goal"
        },
        20
    )

    assert result["status"] == "unavailable"
    assert result["reason"] == "experiment_not_configured"


def test_full_cycle():
    experiment = FakeExperiment(
        result=15
    )

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

    result = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert result["status"] == "completed"
    assert result["goal"] == "reduce_prediction_error"
    assert result["prediction"] == 10
    assert result["actual"] == 15
    assert result["difference"] == 5
    assert result["learning"]["error"] == 5
    assert isinstance(
        result["world_model"],
        dict
    )
    assert result["cycle"]["cycle"] == 1
    assert result["hypothesis_learning"]["status"] == "recorded"


def test_previous_experience_changes_prediction():
    experiment = FakeExperiment(
        result=15
    )

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

    first = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

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

    assert second["prediction"] == 25
    assert second["actual"] == 25
    assert second["difference"] == 0


def test_world_model_receives_result():
    experiment = FakeExperiment(
        result=15
    )

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

    result = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    state = (
        engine.experiment_loop
        .closed_loop
        .experience_learning
        .get_world_state()
    )

    assert result["status"] == "completed"
    assert result["world_model"]["actual"] == 15
    assert state["actual"] == 15


def test_history_is_preserved():
    experiment = FakeExperiment(
        result=15
    )

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

    engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    history = engine.get_history()

    assert len(history) == 1
    assert history[0]["actual"] == 15


def test_stop():
    experiment = FakeExperiment(
        result=15
    )

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

    result = engine.stop()

    assert result["status"] == "stopped"
    assert engine.is_stopped() is True


def test_reset():
    experiment = FakeExperiment(
        result=15
    )

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

    engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    engine.stop()

    result = engine.reset()

    assert result["status"] == "reset"
    assert engine.get_cycle_count() == 0
    assert engine.is_stopped() is False


def test_invalid_goal():
    engine = CognitiveExperimentEngine()

    result = engine.run_cycle(
        None,
        10
    )

    assert result["status"] == "failed"
    assert result["reason"] == "hypothesis_generation_failed"


def test_configuration():
    engine = CognitiveExperimentEngine()

    configuration = engine.get_configuration()

    assert configuration["hypothesis_planner"] == (
        "HypothesisPlanningEngine"
    )
    assert configuration["experiment_loop"] == (
        "ExperimentLoopEngine"
    )


def test_selected_hypothesis_reaches_experiment():
    experiment = HypothesisAwareExperiment(
        result=15
    )

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

    result = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert result["status"] == "completed"
    assert experiment.received_observation == 10

    assert experiment.received_hypothesis == {
        "hypothesis": "use_recent_experience",
        "priority": 3
    }


def test_selected_hypothesis_is_recorded():
    experiment = HypothesisAwareExperiment(
        result=20
    )

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

    result = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert result["difference"] == 10

    learned = engine.get_learned_hypotheses()

    assert len(learned) == 1
    assert learned[0]["hypothesis"] == (
        "use_recent_experience"
    )
    assert learned[0]["attempts"] == 1
    assert learned[0]["average_error"] == 10


def test_better_learned_hypothesis_is_selected():
    experiment = HypothesisAwareExperiment(
        result=10
    )

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

    planner = engine.hypothesis_planner

    planner.record_result(
        "use_recent_experience",
        10
    )

    planner.record_result(
        "increase_observation_frequency",
        2
    )

    reasoning = engine.reason(
        {
            "goal": "reduce_prediction_error"
        }
    )

    selected = reasoning["selected_hypothesis"]

    assert selected["hypothesis"] == (
        "increase_observation_frequency"
    )
    assert selected["learned"] is True
    assert selected["average_error"] == 2
    assert selected["attempts"] == 1


def test_selected_learned_hypothesis_is_sent_to_experiment():
    experiment = HypothesisAwareExperiment(
        result=10
    )

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

    planner = engine.hypothesis_planner

    planner.record_result(
        "use_recent_experience",
        10
    )

    planner.record_result(
        "increase_observation_frequency",
        2
    )

    result = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert result["status"] == "completed"

    assert (
        result["selected_hypothesis"]["hypothesis"]
        == "increase_observation_frequency"
    )

    assert (
        experiment.received_hypothesis["hypothesis"]
        == "increase_observation_frequency"
    )


def test_hypothesis_learning_result_is_returned():
    experiment = HypothesisAwareExperiment(
        result=15
    )

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

    result = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert "hypothesis_learning" in result
    assert result["hypothesis_learning"]["status"] == (
        "recorded"
    )
    assert result["hypothesis_learning"]["hypothesis"] == (
        "use_recent_experience"
    )
    assert result["hypothesis_learning"]["attempts"] == 1
    assert result["hypothesis_learning"]["average_error"] == 5


def test_hypothesis_learning_improves_selection_across_cycles():
    experiment = HypothesisAwareExperiment(
        result=20
    )

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

    first = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert first["status"] == "completed"
    assert first["selected_hypothesis"]["hypothesis"] == (
        "use_recent_experience"
    )
    assert first["difference"] == 10

    planner = engine.hypothesis_planner

    planner.record_result(
        "increase_observation_frequency",
        2
    )

    reasoning = engine.reason(
        {
            "goal": "reduce_prediction_error"
        }
    )

    selected = reasoning["selected_hypothesis"]

    assert selected["hypothesis"] == (
        "increase_observation_frequency"
    )
    assert selected["learned"] is True
    assert selected["average_error"] == 2

    assert selected["attempts"] == 1

    assert selected["score"] == 1 / (1 + 2)


def test_learned_hypothesis_is_used_again_in_next_cycle():
    experiment = HypothesisAwareExperiment(
        result=10
    )

    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = experiment

    planner = engine.hypothesis_planner

    planner.record_result(
        "use_recent_experience",
        10
    )

    planner.record_result(
        "increase_observation_frequency",
        2
    )

    first = engine.run_cycle(
        {
            "goal": "reduce_prediction_error"
        },
        10
    )

    assert first["status"] == "completed"
    assert first["selected_hypothesis"]["hypothesis"] == (
        "increase_observation_frequency"
    )

    assert experiment.received_hypothesis["hypothesis"] == (
        "increase_observation_frequency"
    )

    learned = engine.get_learned_hypotheses()

    selected_record = None

    for record in learned:
        if record["hypothesis"] == (
            "increase_observation_frequency"
        ):
            selected_record = record
            break

    assert selected_record is not None
    assert selected_record["attempts"] == 2
    assert selected_record["average_error"] == 2
