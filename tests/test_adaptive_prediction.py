from core.prediction import PredictionEngine
from core.memory import MemoryEngine
from core.adaptive_prediction import AdaptivePredictionEngine


def test_adaptive_prediction_without_memory():

    predictor = PredictionEngine()
    memory = MemoryEngine()

    adaptive = AdaptivePredictionEngine(
        predictor,
        memory
    )

    result = adaptive.predict(10)

    assert result == 10


def test_adaptive_prediction_uses_previous_experience():

    predictor = PredictionEngine()
    memory = MemoryEngine()

    memory.store({
        "observation": 10,
        "prediction": 10,
        "actual": 15,
        "difference": 5
    })

    adaptive = AdaptivePredictionEngine(
        predictor,
        memory
    )

    result = adaptive.predict(20)

    # Base prediction = 20
    # Previous error = 5
    # Adaptive prediction = 25
    assert result == 25


def test_adaptive_prediction_uses_average_error():

    predictor = PredictionEngine()
    memory = MemoryEngine()

    memory.store({
        "observation": 10,
        "prediction": 10,
        "actual": 14,
        "difference": 4
    })

    memory.store({
        "observation": 20,
        "prediction": 20,
        "actual": 26,
        "difference": 6
    })

    adaptive = AdaptivePredictionEngine(
        predictor,
        memory
    )

    result = adaptive.predict(30)

    # Average previous error = (4 + 6) / 2 = 5
    # Base prediction = 30
    # Adaptive prediction = 35
    assert result == 35
