"""
Sudha AI - Cognitive Pipeline Learning Integration Tests

Step 42-D-2

Verifies the complete learning path:

Observation
    ↓
Prediction
    ↓
Actual Outcome
    ↓
Difference
    ↓
Learning Signal
"""

from core.cognitive_pipeline import CognitivePipeline


def test_learning_integration_zero_error():
    pipeline = CognitivePipeline()

    result = pipeline.run_with_actual(
        actual={"text": "test"},
        text="test"
    )

    assert result["status"] == "completed"
    assert result["comparison"]["difference"] == 0
    assert result["learning"]["status"] == "learned"
    assert result["learning"]["result"]["error"] == 0
    assert result["learning"]["result"]["learning_signal"] == 0


def test_learning_integration_numeric_error():
    pipeline = CognitivePipeline()

    result = pipeline.run_with_actual(
        actual=10,
        text="5"
    )

    assert result["status"] == "completed"
    assert result["comparison"]["difference"] == 1
    assert result["learning"]["status"] == "learned"
    assert result["learning"]["result"]["error"] == 1
    assert result["learning"]["result"]["learning_signal"] == 1


def test_learning_integration_preserves_prediction():
    pipeline = CognitivePipeline()

    result = pipeline.run_with_actual(
        actual={"text": "different"},
        text="original"
    )

    assert result["status"] == "completed"
    assert "prediction" in result
    assert "comparison" in result
    assert "learning" in result


def test_learning_integration_contains_complete_cycle():
    pipeline = CognitivePipeline()

    result = pipeline.run_with_actual(
        actual="observed",
        text="input"
    )

    assert result["status"] == "completed"

    assert "observation" in result
    assert "prediction" in result
    assert "comparison" in result
    assert "learning" in result

    assert result["observation"]["status"] == (
        "observation_created"
    )

    assert result["prediction"]["status"] == (
        "predicted"
    )

    assert result["comparison"]["status"] == (
        "compared"
    )

    assert result["learning"]["status"] == (
        "learned"
    )


def test_learning_signal_matches_difference():
    pipeline = CognitivePipeline()

    result = pipeline.run_with_actual(
        actual={"text": "different"},
        text="input"
    )

    difference = result["comparison"]["difference"]

    learning_signal = (
        result["learning"]["result"]["learning_signal"]
    )

    assert learning_signal == difference
