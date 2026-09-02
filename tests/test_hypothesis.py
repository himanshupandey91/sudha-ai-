from core.hypothesis import HypothesisEngine


def test_hypothesis_generation_for_prediction_error():

    engine = HypothesisEngine()

    result = engine.generate({
        "goal": "reduce_prediction_error",
        "priority": 5
    })

    assert len(result) == 3

    assert result[0]["hypothesis"] == "use_recent_experience"
    assert result[0]["priority"] == 3

    assert result[1]["hypothesis"] == "increase_observation_frequency"
    assert result[1]["priority"] == 2

    assert result[2]["hypothesis"] == "change_prediction_strategy"
    assert result[2]["priority"] == 1


def test_hypothesis_ranking():

    engine = HypothesisEngine()

    result = engine.best({
        "goal": "reduce_prediction_error",
        "priority": 5
    })

    assert result["hypothesis"] == "use_recent_experience"
    assert result["priority"] == 3


def test_hypothesis_generation_for_observation():

    engine = HypothesisEngine()

    result = engine.generate({
        "goal": "continue_observation",
        "priority": 0
    })

    assert len(result) == 1
    assert result[0]["hypothesis"] == "collect_more_observations"


def test_unknown_goal_generates_information_hypothesis():

    engine = HypothesisEngine()

    result = engine.generate({
        "goal": "unknown_goal",
        "priority": 1
    })

    assert len(result) == 1
    assert result[0]["hypothesis"] == "collect_more_information"


def test_hypothesis_limit():

    engine = HypothesisEngine(
        max_hypotheses=2
    )

    result = engine.generate({
        "goal": "reduce_prediction_error",
        "priority": 5
    })

    assert len(result) == 2
