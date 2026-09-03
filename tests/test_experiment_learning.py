from core.experiment_learning import (
    ExperimentLearningEngine
)


def create_engine():
    return ExperimentLearningEngine()


def test_learning_records_successful_experiment():

    engine = create_engine()

    result = engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "test_hypothesis",
            "predicted_difference": 0
        }
    )

    assert result["status"] == "learned"
    assert result["record"]["hypothesis"] == (
        "test_hypothesis"
    )
    assert result["record"]["predicted_difference"] == 0
    assert result["record"]["outcome"] == "success"
    assert result["record_count"] == 1


def test_learning_records_partial_result():

    engine = create_engine()

    result = engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "test_hypothesis",
            "predicted_difference": 5
        }
    )

    assert result["status"] == "learned"
    assert result["record"]["outcome"] == "partial"


def test_learning_rejects_invalid_evaluation():

    engine = create_engine()

    try:
        engine.learn("invalid")

        assert False

    except TypeError as error:
        assert str(error) == (
            "evaluation must be a dictionary"
        )


def test_learning_rejects_unevaluated_result():

    engine = create_engine()

    result = engine.learn(
        {
            "status": "rejected",
            "hypothesis": "test_hypothesis",
            "predicted_difference": 5
        }
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "evaluation_not_valid"
    )


def test_learning_rejects_invalid_hypothesis():

    engine = create_engine()

    result = engine.learn(
        {
            "status": "evaluated",
            "hypothesis": 123,
            "predicted_difference": 5
        }
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "hypothesis_must_be_a_string"
    )


def test_learning_rejects_invalid_difference():

    engine = create_engine()

    result = engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "test_hypothesis",
            "predicted_difference": "invalid"
        }
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "predicted_difference_must_be_numeric"
    )


def test_best_hypothesis():

    engine = create_engine()

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "hypothesis_a",
            "predicted_difference": 8
        }
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "hypothesis_b",
            "predicted_difference": 3
        }
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "hypothesis_c",
            "predicted_difference": 6
        }
    )

    assert engine.best_hypothesis() == (
        "hypothesis_b"
    )


def test_hypothesis_performance():

    engine = create_engine()

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "hypothesis_a",
            "predicted_difference": 8
        }
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "hypothesis_a",
            "predicted_difference": 4
        }
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "hypothesis_b",
            "predicted_difference": 6
        }
    )

    assert engine.hypothesis_performance() == {
        "hypothesis_a": 4,
        "hypothesis_b": 6
    }


def test_learning_memory_is_bounded():

    engine = ExperimentLearningEngine(
        max_records=2
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "a",
            "predicted_difference": 10
        }
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "b",
            "predicted_difference": 5
        }
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "c",
            "predicted_difference": 2
        }
    )

    assert engine.size() == 2

    assert engine.retrieve_all() == [
        {
            "hypothesis": "b",
            "predicted_difference": 5,
            "outcome": "partial"
        },
        {
            "hypothesis": "c",
            "predicted_difference": 2,
            "outcome": "partial"
        }
    ]


def test_learning_clear():

    engine = create_engine()

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "test",
            "predicted_difference": 5
        }
    )

    result = engine.clear()

    assert result["status"] == "cleared"
    assert result["record_count"] == 0
    assert engine.size() == 0
