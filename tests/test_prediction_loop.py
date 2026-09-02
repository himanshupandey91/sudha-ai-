from core.prediction_loop import PredictionLoop


def test_prediction_loop():

    system = PredictionLoop()

    result = system.process(
        observation=10,
        actual=15
    )

    # Prediction
    assert result["prediction"] == 10

    # Difference
    assert result["difference"] == 5

    # Attention
    assert result["attention"]["focus"] == "prediction_error"
    assert result["attention"]["value"] == 5

    # Learning
    assert result["learning"]["error"] == 5
    assert result["learning"]["learning_signal"] == 5

    # Curiosity
    assert result["curiosity"]["difference"] == 5
    assert result["curiosity"]["curiosity"] == 5

    # World Model
    assert result["observation"] == 10
    assert result["prediction"] == 10
    assert result["actual"] == 15
    assert result["difference"] == 5
