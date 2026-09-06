"""
Sudha AI - Experience Learning Tests

Version 0.2

Tests the complete experience-learning cycle:

Prediction
    ↓
Actual Outcome
    ↓
Difference
    ↓
Learning
    ↓
Memory
    ↓
Adaptive Prediction
"""


from core.experience_learning import (
    ExperienceLearningEngine
)


def test_prediction_without_actual():
    """
    The engine should generate a prediction
    without inventing an actual outcome.
    """

    engine = ExperienceLearningEngine()

    result = engine.run(
        observation=10
    )

    assert result["status"] == "predicted"
    assert result["observation"] == 10
    assert result["prediction"] == 10

    assert "actual" not in result


def test_complete_learning_cycle():
    """
    A real actual outcome should produce:

    prediction
    difference
    learning signal
    memory
    """

    engine = ExperienceLearningEngine()

    result = engine.run(
        observation=10,
        actual=15
    )

    assert result["status"] == "completed"

    assert result["observation"] == 10
    assert result["prediction"] == 10
    assert result["actual"] == 15
    assert result["difference"] == 5

    assert result["learning"]["error"] == 5
    assert result["learning"]["learning_signal"] == 5

    assert result["memory"]["status"] == "stored"

    assert (
        result["memory"]["memory"]["observation"]
        == 10
    )

    assert (
        result["memory"]["memory"]["prediction"]
        == 10
    )

    assert (
        result["memory"]["memory"]["actual"]
        == 15
    )

    assert (
        result["memory"]["memory"]["difference"]
        == 5
    )


def test_experience_changes_future_prediction():
    """
    Previous prediction error should influence
    a future prediction.
    """

    engine = ExperienceLearningEngine()

    first = engine.run(
        observation=10,
        actual=15
    )

    assert first["difference"] == 5

    second = engine.run(
        observation=20
    )

    assert second["status"] == "predicted"

    assert second["prediction"] == 25


def test_exact_previous_experience_is_reused():
    """
    An exact previous observation should use
    its stored experience.
    """

    engine = ExperienceLearningEngine()

    engine.run(
        observation=10,
        actual=15
    )

    result = engine.run(
        observation=10
    )

    assert result["status"] == "predicted"
    assert result["prediction"] == 15


def test_multiple_experiences_update_prediction():
    """
    Multiple historical experiences should
    progressively influence future prediction.

    First:
        10 → 14
        error = 4

    Second:
        base = 20
        historical error = 4
        prediction = 24
        actual = 26
        error = 2

    Historical average after both:
        (4 + 2) / 2 = 3

    Therefore:
        30 + 3 = 33
    """

    engine = ExperienceLearningEngine()

    first = engine.run(
        observation=10,
        actual=14
    )

    assert first["prediction"] == 10
    assert first["difference"] == 4

    second = engine.run(
        observation=20,
        actual=26
    )

    assert second["prediction"] == 24
    assert second["difference"] == 2

    result = engine.run(
        observation=30
    )

    assert result["status"] == "predicted"
    assert result["prediction"] == 33


def test_memory_contains_learning_history():
    """
    Learning experiences should remain available
    through the memory interface.

    The second experience can have zero error
    because adaptive prediction may correctly
    predict the actual outcome.
    """

    engine = ExperienceLearningEngine()

    engine.run(
        observation=10,
        actual=15
    )

    engine.run(
        observation=20,
        actual=25
    )

    memories = engine.get_memory()

    assert len(memories) == 2

    assert memories[0]["observation"] == 10
    assert memories[0]["actual"] == 15
    assert memories[0]["difference"] == 5

    assert memories[1]["observation"] == 20
    assert memories[1]["prediction"] == 25
    assert memories[1]["actual"] == 25
    assert memories[1]["difference"] == 0


def test_memory_size():
    """
    Memory size should reflect stored experiences.
    """

    engine = ExperienceLearningEngine()

    assert engine.get_memory_size() == 0

    engine.run(
        observation=10,
        actual=15
    )

    assert engine.get_memory_size() == 1

    engine.run(
        observation=20,
        actual=25
    )

    assert engine.get_memory_size() == 2


def test_clear_memory():
    """
    Clearing memory should remove stored experiences.
    """

    engine = ExperienceLearningEngine()

    engine.run(
        observation=10,
        actual=15
    )

    assert engine.get_memory_size() == 1

    result = engine.clear_memory()

    assert result["status"] == "cleared"
    assert engine.get_memory_size() == 0
    assert engine.get_memory() == []
