"""
Sudha AI - Cognitive Pipeline Tests

Version 0.1

Tests the integrated cognitive pipeline:

Perception
    ↓
Observation
    ↓
Prediction
    ↓
Actual Outcome
    ↓
Difference
"""

from core.cognitive_pipeline import CognitivePipeline


def test_pipeline_can_be_created():
    pipeline = CognitivePipeline()

    assert pipeline is not None


def test_pipeline_observes_text():
    pipeline = CognitivePipeline()

    result = pipeline.observe(
        text="hello"
    )

    assert result["status"] == "observation_created"
    assert "text" in result["modalities"]
    assert result["data"]["text"] == "hello"


def test_pipeline_observes_multiple_modalities():
    pipeline = CognitivePipeline()

    result = pipeline.observe(
        text="hello",
        voice=b"audio",
        image=b"image",
        video=b"video"
    )

    assert result["status"] == "observation_created"
    assert result["count"] == 4

    assert "text" in result["modalities"]
    assert "voice" in result["modalities"]
    assert "image" in result["modalities"]
    assert "video" in result["modalities"]


def test_pipeline_predicts_from_observation():
    pipeline = CognitivePipeline()

    observation = pipeline.observe(
        text="hello"
    )

    result = pipeline.predict(
        observation
    )

    assert result["status"] == "predicted"
    assert "prediction" in result


def test_pipeline_rejects_invalid_observation():
    pipeline = CognitivePipeline()

    result = pipeline.predict(
        "invalid"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "observation_must_be_a_dictionary"
    )


def test_pipeline_run_returns_prediction():
    pipeline = CognitivePipeline()

    result = pipeline.run(
        text="hello"
    )

    assert result["status"] == "predicted"
    assert "observation" in result
    assert "prediction" in result


def test_pipeline_run_does_not_create_fake_actual():
    pipeline = CognitivePipeline()

    result = pipeline.run(
        text="hello"
    )

    assert "comparison" not in result


def test_pipeline_compare_numeric_values():
    pipeline = CognitivePipeline()

    result = pipeline.compare(
        prediction=10,
        actual=13
    )

    assert result["status"] == "compared"
    assert result["prediction"] == 10
    assert result["actual"] == 13
    assert result["difference"] == 3


def test_pipeline_run_with_actual():
    pipeline = CognitivePipeline()

    result = pipeline.run_with_actual(
        actual="hello",
        text="hello"
    )

    assert result["status"] == "completed"
    assert "observation" in result
    assert "prediction" in result
    assert "comparison" in result


def test_pipeline_run_with_actual_contains_difference():
    pipeline = CognitivePipeline()

    result = pipeline.run_with_actual(
        actual="different",
        text="hello"
    )

    comparison = result["comparison"]

    assert comparison["status"] == "compared"
    assert "difference" in comparison


def test_pipeline_rejects_empty_multimodal_input():
    pipeline = CognitivePipeline()

    result = pipeline.run()

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "perceptions_cannot_be_empty"
    )
