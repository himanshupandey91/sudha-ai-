def test_hypothesis_statistics():

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
            "hypothesis": "hypothesis_a",
            "predicted_difference": 0
        }
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "hypothesis_b",
            "predicted_difference": 6
        }
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "hypothesis_b",
            "predicted_difference": 2
        }
    )

    statistics = (
        engine.hypothesis_statistics()
    )

    assert statistics == {
        "hypothesis_a": {
            "tests": 3,
            "best": 0,
            "average": 4.0,
            "latest": 0,
            "success": 1,
            "partial": 2
        },
        "hypothesis_b": {
            "tests": 2,
            "best": 2,
            "average": 4.0,
            "latest": 2,
            "success": 0,
            "partial": 2
        }
    }


def test_hypothesis_statistics_empty():

    engine = create_engine()

    assert engine.hypothesis_statistics() == {}


def test_hypothesis_statistics_tracks_latest_result():

    engine = create_engine()

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "test_hypothesis",
            "predicted_difference": 10
        }
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "test_hypothesis",
            "predicted_difference": 3
        }
    )

    statistics = (
        engine.hypothesis_statistics()
    )

    assert statistics[
        "test_hypothesis"
    ]["latest"] == 3


def test_hypothesis_statistics_tracks_best_result():

    engine = create_engine()

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "test_hypothesis",
            "predicted_difference": 10
        }
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "test_hypothesis",
            "predicted_difference": 2
        }
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "test_hypothesis",
            "predicted_difference": 7
        }
    )

    statistics = (
        engine.hypothesis_statistics()
    )

    assert statistics[
        "test_hypothesis"
    ]["best"] == 2


def test_hypothesis_statistics_tracks_success_and_partial():

    engine = create_engine()

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "test_hypothesis",
            "predicted_difference": 0
        }
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "test_hypothesis",
            "predicted_difference": 5
        }
    )

    engine.learn(
        {
            "status": "evaluated",
            "hypothesis": "test_hypothesis",
            "predicted_difference": 0
        }
    )

    statistics = (
        engine.hypothesis_statistics()
    )

    assert statistics[
        "test_hypothesis"
    ]["success"] == 2

    assert statistics[
        "test_hypothesis"
    ]["partial"] == 1
