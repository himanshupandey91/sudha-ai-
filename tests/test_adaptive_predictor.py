"""
Sudha AI - Adaptive Predictor Tests

Step 61-B

Validates:

Prediction
    ↓
Observed Result
    ↓
Adaptive Update
    ↓
Improved Future Prediction
"""

from core.adaptive_predictor import AdaptivePredictor


def test_new_hypothesis_learns_first_observation():
    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    result = predictor.update(
        "hypothesis_a",
        10
    )

    assert result["status"] == "updated"
    assert result["hypothesis"] == "hypothesis_a"
    assert result["actual"] == 10
    assert result["prediction"] == 10

    assert predictor.predict(
        "hypothesis_a"
    ) == 10


def test_prediction_moves_toward_actual_result():
    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    predictor.update(
        "hypothesis_a",
        10
    )

    result = predictor.update(
        "hypothesis_a",
        20
    )

    assert result["prediction"] == 15

    assert predictor.predict(
        "hypothesis_a"
    ) == 15


def test_repeated_learning_converges_toward_actual():
    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    predictor.update(
        "hypothesis_a",
        10
    )

    predictor.update(
        "hypothesis_a",
        20
    )

    predictor.update(
        "hypothesis_a",
        20
    )

    assert predictor.predict(
        "hypothesis_a"
    ) == 17.5


def test_different_hypotheses_learn_independently():
    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    predictor.update(
        "hypothesis_a",
        10
    )

    predictor.update(
        "hypothesis_b",
        30
    )

    assert predictor.predict(
        "hypothesis_a"
    ) == 10

    assert predictor.predict(
        "hypothesis_b"
    ) == 30


def test_unseen_hypothesis_returns_none():
    predictor = AdaptivePredictor()

    assert predictor.predict(
        "unknown"
    ) is None


def test_history_records_learning():
    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    predictor.update(
        "hypothesis_a",
        10
    )

    predictor.update(
        "hypothesis_a",
        20
    )

    history = predictor.get_history(
        "hypothesis_a"
    )

    assert len(history) == 2
    assert history[0]["actual"] == 10
    assert history[1]["actual"] == 20


def test_clear_removes_learning():
    predictor = AdaptivePredictor()

    predictor.update(
        "hypothesis_a",
        10
    )

    result = predictor.clear()

    assert result["status"] == "cleared"

    assert predictor.predict(
        "hypothesis_a"
    ) is None

    assert predictor.get_history(
        "hypothesis_a"
    ) == []
