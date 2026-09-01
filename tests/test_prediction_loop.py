from core.prediction_loop import PredictionLoop


def test_prediction_loop():

    system = PredictionLoop()

    result = system.process(
        observation=10,
        actual=15
    )

    assert result["prediction"] == 10
    assert result["difference"] == 5
