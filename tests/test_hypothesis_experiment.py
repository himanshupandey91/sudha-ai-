from core.hypothesis_experiment import HypothesisExperiment


def test_experiment_accepts_selected_hypothesis():
    experiment = HypothesisExperiment(target=10)

    hypothesis = {
        "hypothesis": "explore_new_pattern",
        "priority": 1
    }

    actual = experiment.run(
        observation=5,
        hypothesis=hypothesis
    )

    assert actual == 10


def test_recent_experience_uses_observation():
    experiment = HypothesisExperiment(target=10)

    hypothesis = {
        "hypothesis": "use_recent_experience",
        "priority": 3
    }

    actual = experiment.run(
        observation=5,
        hypothesis=hypothesis
    )

    assert actual == 5


def test_conservative_estimate():
    experiment = HypothesisExperiment(target=10)

    hypothesis = {
        "hypothesis": "conservative_estimate",
        "priority": 2
    }

    actual = experiment.run(
        observation=10,
        hypothesis=hypothesis
    )

    assert actual == 5


def test_history_records_experiment():
    experiment = HypothesisExperiment(target=10)

    hypothesis = {
        "hypothesis": "explore_new_pattern",
        "priority": 1
    }

    experiment.run(
        observation=5,
        hypothesis=hypothesis
    )

    history = experiment.get_history()

    assert len(history) == 1
    assert history[0]["hypothesis"] == "explore_new_pattern"
    assert history[0]["actual"] == 10


def test_clear_history():
    experiment = HypothesisExperiment(target=10)

    hypothesis = {
        "hypothesis": "explore_new_pattern",
        "priority": 1
    }

    experiment.run(
        observation=5,
        hypothesis=hypothesis
    )

    experiment.clear_history()

    assert experiment.get_history() == []


def test_configuration():
    experiment = HypothesisExperiment(target=10)

    configuration = experiment.get_configuration()

    assert configuration["target"] == 10
    assert configuration["history_size"] == 0
