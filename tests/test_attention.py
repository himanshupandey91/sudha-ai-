from core.attention import AttentionEngine


def test_attention_focuses_on_prediction_error():

    engine = AttentionEngine()

    state = {
        "observation": 10,
        "prediction": 10,
        "actual": 15,
        "difference": 5
    }

    result = engine.focus(state)

    assert result["focus"] == "prediction_error"
    assert result["value"] == 5
