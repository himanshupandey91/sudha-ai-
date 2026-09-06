from core.hypothesis_learning import (
    HypothesisLearningEngine
)


def test_record_first_attempt():
    engine = HypothesisLearningEngine()

    result = engine.record(
        "use_recent_experience",
        5
    )

    assert result["status"] == "recorded"
    assert result["hypothesis"] == (
        "use_recent_experience"
    )
    assert result["attempts"] == 1
    assert result["average_error"] == 5
    assert result["score"] == 1 / 6


def test_record_multiple_attempts():
    engine = HypothesisLearningEngine()

    engine.record(
        "use_recent_experience",
        5
    )

    result = engine.record(
        "use_recent_experience",
        3
    )

    assert result["attempts"] == 2
    assert result["average_error"] == 4
    assert result["score"] == 1 / 5


def test_different_hypotheses_are_tracked_separately():
    engine = HypothesisLearningEngine()

    first = engine.record(
        "use_recent_experience",
        2
    )

    second = engine.record(
        "change_prediction_strategy",
        8
    )

    assert first["hypothesis"] == (
        "use_recent_experience"
    )

    assert second["hypothesis"] == (
        "change_prediction_strategy"
    )

    assert engine.size() == 2


def test_evaluate_seen_hypothesis():
    engine = HypothesisLearningEngine()

    engine.record(
        "use_recent_experience",
        4
    )

    result = engine.evaluate(
        "use_recent_experience"
    )

    assert result["hypothesis"] == (
        "use_recent_experience"
    )
    assert result["attempts"] == 1
    assert result["average_error"] == 4
    assert result["score"] == 1 / 5


def test_evaluate_unseen_hypothesis():
    engine = HypothesisLearningEngine()

    result = engine.evaluate(
        "new_hypothesis"
    )

    assert result["status"] == "unseen"
    assert result["hypothesis"] == (
        "new_hypothesis"
    )
    assert result["attempts"] == 0
    assert result["average_error"] is None
    assert result["score"] == 0


def test_rank_hypotheses():
    engine = HypothesisLearningEngine()

    engine.record(
        "bad_hypothesis",
        10
    )

    engine.record(
        "good_hypothesis",
        2
    )

    engine.record(
        "medium_hypothesis",
        5
    )

    ranked = engine.rank()

    assert len(ranked) == 3

    assert ranked[0]["hypothesis"] == (
        "good_hypothesis"
    )

    assert ranked[1]["hypothesis"] == (
        "medium_hypothesis"
    )

    assert ranked[2]["hypothesis"] == (
        "bad_hypothesis"
    )


def test_best_hypothesis():
    engine = HypothesisLearningEngine()

    engine.record(
        "hypothesis_a",
        7
    )

    engine.record(
        "hypothesis_b",
        2
    )

    best = engine.best()

    assert best["hypothesis"] == (
        "hypothesis_b"
    )

    assert best["average_error"] == 2


def test_get_records():
    engine = HypothesisLearningEngine()

    engine.record(
        "hypothesis_a",
        3
    )

    engine.record(
        "hypothesis_b",
        6
    )

    records = engine.get_records()

    assert len(records) == 2

    names = {
        record["hypothesis"]
        for record in records
    }

    assert names == {
        "hypothesis_a",
        "hypothesis_b"
    }


def test_clear():
    engine = HypothesisLearningEngine()

    engine.record(
        "hypothesis_a",
        3
    )

    engine.record(
        "hypothesis_b",
        6
    )

    result = engine.clear()

    assert result["status"] == "cleared"
    assert result["count"] == 0
    assert engine.size() == 0
    assert engine.best() is None


def test_configuration():
    engine = HypothesisLearningEngine()

    engine.record(
        "hypothesis_a",
        4
    )

    configuration = (
        engine.get_configuration()
    )

    assert configuration[
        "hypothesis_count"
    ] == 1


def test_invalid_hypothesis_type():
    engine = HypothesisLearningEngine()

    try:
        engine.record(
            123,
            5
        )
        assert False
    except TypeError:
        assert True


def test_empty_hypothesis():
    engine = HypothesisLearningEngine()

    try:
        engine.record(
            "",
            5
        )
        assert False
    except ValueError:
        assert True


def test_invalid_difference_type():
    engine = HypothesisLearningEngine()

    try:
        engine.record(
            "hypothesis",
            "bad"
        )
        assert False
    except TypeError:
        assert True
