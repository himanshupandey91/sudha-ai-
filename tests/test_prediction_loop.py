from core.prediction_loop import PredictionLoop


def test_prediction_loop():

    system = PredictionLoop()

    result = system.process(
        observation=10,
        actual=15
    )

    assert result["prediction"] == 10
    assert result["difference"] == 5

    assert result["attention"]["focus"] == "prediction_error"
    assert result["attention"]["value"] == 5

    assert result["learning"]["error"] == 5
    assert result["learning"]["learning_signal"] == 5

    assert result["curiosity"]["difference"] == 5
    assert result["curiosity"]["curiosity"] == 5
