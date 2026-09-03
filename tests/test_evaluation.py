from core.evaluation import EvaluationEngine


def create_engine():
    return EvaluationEngine()


def test_evaluation_calculates_score():

    engine = create_engine()

    result = engine.evaluate(
        {
            "experiment": 1,
            "hypothesis": "use_recent_experience",
            "result": {
                "status": "completed",
                "predicted_difference": 5
            }
        }
    )

    assert result["status"] == "evaluated"
    assert result["hypothesis"] == "use_recent_experience"
    assert result["predicted_difference"] == 5
    assert result["score"] == -5


def test_lower_prediction_error_is_better():

    engine = create_engine()

    first = {
        "predicted_difference": 5
    }

    second = {
        "predicted_difference": 10
    }

    assert engine.better(
        first,
        second
    ) is True


def test_higher_prediction_error_is_not_better():

    engine = create_engine()

    first = {
        "predicted_difference": 10
    }

    second = {
        "predicted_difference": 5
    }

    assert engine.better(
        first,
        second
    ) is False


def test_evaluation_rejects_invalid_experiment():

    engine = create_engine()

    try:
        engine.evaluate("invalid")

        assert False

    except TypeError as error:
        assert str(error) == (
            "experiment_result must be a dictionary"
        )


def test_evaluation_rejects_invalid_result():

    engine = create_engine()

    result = engine.evaluate(
        {
            "experiment": 1,
            "hypothesis": "test",
            "result": "invalid"
        }
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "result_must_be_a_dictionary"
    )


def test_evaluation_rejects_non_numeric_difference():

    engine = create_engine()

    result = engine.evaluate(
        {
            "experiment": 1,
            "hypothesis": "test",
            "result": {
                "status": "completed",
                "predicted_difference": "invalid"
            }
        }
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "predicted_difference_must_be_numeric"
    )


def test_better_handles_invalid_first_result():

    engine = create_engine()

    result = engine.better(
        {
            "predicted_difference": "invalid"
        },
        {
            "predicted_difference": 5
        }
    )

    assert result is False


def test_better_handles_invalid_second_result():

    engine = create_engine()

    result = engine.better(
        {
            "predicted_difference": 5
        },
        {
            "predicted_difference": "invalid"
        }
    )

    assert result is True
