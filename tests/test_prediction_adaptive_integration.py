"""
Sudha AI - Prediction / Adaptive Predictor Integration Tests

Step 61-F

Validates:

Static Prediction
    ↓
Adaptive Predictor
    ↓
Prediction
    ↓
Actual Result
    ↓
Prediction Error
    ↓
Gradual Adaptive Learning
"""


from core.prediction import PredictionEngine
from core.adaptive_predictor import AdaptivePredictor


def test_prediction_engine_uses_adaptive_prediction():
    adaptive = AdaptivePredictor(
        learning_rate=0.5
    )

    engine = PredictionEngine(
        hypothesis_predictions={
            "hypothesis_a": 10
        },
        adaptive_predictor=adaptive
    )

    assert engine.predict(
        0,
        hypothesis="hypothesis_a"
    ) == 10

    adaptive.update(
        "hypothesis_a",
        20
    )

    assert engine.predict(
        0,
        hypothesis="hypothesis_a"
    ) == 15


def test_prediction_engine_learns_from_actual_result():
    adaptive = AdaptivePredictor(
        learning_rate=0.5
    )

    engine = PredictionEngine(
        hypothesis_predictions={
            "hypothesis_a": 10
        },
        adaptive_predictor=adaptive
    )

    result = engine.learn(
        "hypothesis_a",
        20
    )

    assert result["status"] == "learned"
    assert result["hypothesis"] == "hypothesis_a"

    assert adaptive.predict(
        "hypothesis_a"
    ) == 15


def test_adaptive_prediction_has_priority_over_static_prediction():
    adaptive = AdaptivePredictor(
        learning_rate=0.5
    )

    adaptive.set_prediction(
        "hypothesis_a",
        10
    )

    adaptive.update(
        "hypothesis_a",
        30
    )

    engine = PredictionEngine(
        hypothesis_predictions={
            "hypothesis_a": 10
        },
        adaptive_predictor=adaptive
    )

    prediction = engine.predict(
        0,
        hypothesis="hypothesis_a"
    )

    assert prediction == 20


def test_unknown_adaptive_hypothesis_falls_back_to_static_prediction():
    adaptive = AdaptivePredictor()

    engine = PredictionEngine(
        hypothesis_predictions={
            "hypothesis_a": 10
        },
        adaptive_predictor=adaptive
    )

    prediction = engine.predict(
        0,
        hypothesis="hypothesis_a"
    )

    assert prediction == 10


def test_update_from_actual_is_alias_for_adaptive_learning():
    adaptive = AdaptivePredictor()

    engine = PredictionEngine(
        adaptive_predictor=adaptive
    )

    result = engine.update_from_actual(
        "hypothesis_a",
        25
    )

    assert result["status"] == "learned"
    assert result["hypothesis"] == "hypothesis_a"

    assert engine.predict(
        0,
        hypothesis="hypothesis_a"
    ) == 25


def test_prediction_moves_gradually_toward_actual():
    adaptive = AdaptivePredictor(
        learning_rate=0.5
    )

    engine = PredictionEngine(
        hypothesis_predictions={
            "hypothesis_a": 10
        },
        adaptive_predictor=adaptive
    )

    first = engine.learn(
        "hypothesis_a",
        20
    )

    assert first["result"]["prediction"] == 15

    second = engine.learn(
        "hypothesis_a",
        20
    )

    assert second["result"]["prediction"] == 17.5

    third = engine.learn(
        "hypothesis_a",
        20
    )

    assert third["result"]["prediction"] == 18.75


def test_adaptive_learning_reports_prediction_error():
    adaptive = AdaptivePredictor(
        learning_rate=0.5
    )

    adaptive.set_prediction(
        "hypothesis_a",
        10
    )

    result = adaptive.update(
        "hypothesis_a",
        20
    )

    assert result["error"] == 10
    assert result["prediction"] == 15


def test_static_prediction_is_used_as_adaptive_initial_state():
    adaptive = AdaptivePredictor(
        learning_rate=0.5
    )

    engine = PredictionEngine(
        hypothesis_predictions={
            "hypothesis_a": 10
        },
        adaptive_predictor=adaptive
    )

    assert adaptive.predict(
        "hypothesis_a"
    ) == 10

    result = engine.learn(
        "hypothesis_a",
        20
    )

    assert result["result"]["prediction"] == 15
