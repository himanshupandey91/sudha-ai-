from core.hypothesis_experiment import HypothesisExperiment


def test_default_outcomes():
    experiment = HypothesisExperiment()

    assert experiment.get_outcomes() == {
        "use_recent_experience": 5,
        "explore_new_pattern": 8,
        "use_world_model": 3,
    }


def test_custom_outcomes():
    experiment = HypothesisExperiment(
        outcomes={
            "hypothesis_a": 5,
            "hypothesis_b": 8,
        }
    )

    assert experiment.get_outcomes() == {
        "hypothesis_a": 5,
        "hypothesis_b": 8,
    }


def test_selected_hypothesis_produces_expected_result():
    experiment = HypothesisExperiment()

    hypothesis = {
        "hypothesis": "explore_new_pattern",
        "priority": 1,
    }

    result = experiment.run(
        observation=10,
        hypothesis=hypothesis,
    )

    assert result["status"] == "experiment_completed"
    assert result["actual"] == 8
    assert result["hypothesis"] == hypothesis


def test_different_hypotheses_produce_different_results():
    experiment = HypothesisExperiment()

    hypothesis_a = {
        "hypothesis": "use_recent_experience",
        "priority": 3,
    }

    hypothesis_b = {
        "hypothesis": "explore_new_pattern",
        "priority": 1,
    }

    result_a = experiment.run(
        observation=10,
        hypothesis=hypothesis_a,
    )

    result_b = experiment.run(
        observation=10,
        hypothesis=hypothesis_b,
    )

    assert result_a["actual"] == 5
    assert result_b["actual"] == 8
    assert result_a["actual"] != result_b["actual"]


def test_hypothesis_is_required():
    experiment = HypothesisExperiment()

    result = experiment.run(
        observation=10,
    )

    assert result["status"] == "failed"
    assert result["reason"] == "hypothesis_required"


def test_invalid_hypothesis():
    experiment = HypothesisExperiment()

    result = experiment.run(
        observation=10,
        hypothesis="explore_new_pattern",
    )

    assert result["status"] == "failed"
    assert result["reason"] == "invalid_hypothesis"


def test_unknown_hypothesis():
    experiment = HypothesisExperiment()

    hypothesis = {
        "hypothesis": "unknown",
        "priority": 1,
    }

    result = experiment.run(
        observation=10,
        hypothesis=hypothesis,
    )

    assert result["status"] == "failed"
    assert result["reason"] == "unknown_hypothesis"
    assert result["hypothesis"] == "unknown"


def test_history_records_completed_experiments():
    experiment = HypothesisExperiment()

    hypothesis = {
        "hypothesis": "use_world_model",
        "priority": 2,
    }

    experiment.run(
        observation=10,
        hypothesis=hypothesis,
    )

    history = experiment.get_history()

    assert len(history) == 1
    assert history[0]["status"] == "experiment_completed"
    assert history[0]["hypothesis"] == hypothesis
    assert history[0]["actual"] == 3


def test_clear_history():
    experiment = HypothesisExperiment()

    hypothesis = {
        "hypothesis": "use_world_model",
        "priority": 2,
    }

    experiment.run(
        observation=10,
        hypothesis=hypothesis,
    )

    experiment.clear_history()

    assert experiment.get_history() == []


def test_get_history_returns_copy():
    experiment = HypothesisExperiment()

    hypothesis = {
        "hypothesis": "use_world_model",
        "priority": 2,
    }

    experiment.run(
        observation=10,
        hypothesis=hypothesis,
    )

    history = experiment.get_history()
    history.clear()

    assert len(experiment.get_history()) == 1


def test_empty_outcomes_rejected():
    try:
        HypothesisExperiment(outcomes={})
        assert False
    except ValueError as error:
        assert str(error) == "outcomes must not be empty"


def test_invalid_outcomes_type_rejected():
    try:
        HypothesisExperiment(outcomes=[])
        assert False
    except ValueError as error:
        assert str(error) == "outcomes must be a dictionary"
