"""
Sudha AI - Learning to Memory Integration Tests

Step 42-D-3

Verifies:

Prediction
    ↓
Difference
    ↓
Learning
    ↓
Memory
"""

from core.cognitive_pipeline import CognitivePipeline
from core.memory import MemoryEngine


def test_learning_result_can_be_stored_in_memory():
    pipeline = CognitivePipeline()
    memory = MemoryEngine()

    result = pipeline.run_with_actual(
        actual={"text": "different"},
        text="input"
    )

    assert result["status"] == "completed"
    assert result["learning"]["status"] == "learned"

    learning_result = result["learning"]["result"]

    stored = memory.store(
        {
            "type": "learning",
            "error": learning_result["error"],
            "learning_signal": (
                learning_result["learning_signal"]
            )
        }
    )

    assert stored["status"] == "stored"


def test_memory_preserves_learning_signal():
    pipeline = CognitivePipeline()
    memory = MemoryEngine()

    result = pipeline.run_with_actual(
        actual={"text": "different"},
        text="input"
    )

    learning_signal = (
        result["learning"]["result"]["learning_signal"]
    )

    memory.store(
        {
            "type": "learning",
            "learning_signal": learning_signal
        }
    )

    memories = memory.retrieve()

    assert len(memories) == 1
    assert memories[0]["type"] == "learning"
    assert (
        memories[0]["learning_signal"]
        == learning_signal
    )


def test_zero_error_learning_can_be_stored():
    pipeline = CognitivePipeline()
    memory = MemoryEngine()

    result = pipeline.run_with_actual(
        actual={"text": "test"},
        text="test"
    )

    assert result["comparison"]["difference"] == 0

    memory.store(
        {
            "type": "learning",
            "error": 0,
            "learning_signal": 0
        }
    )

    memories = memory.retrieve()

    assert memories[0]["error"] == 0
    assert memories[0]["learning_signal"] == 0


def test_multiple_learning_experiences_are_preserved():
    pipeline = CognitivePipeline()
    memory = MemoryEngine()

    first = pipeline.run_with_actual(
        actual={"text": "one"},
        text="one"
    )

    second = pipeline.run_with_actual(
        actual={"text": "different"},
        text="two"
    )

    memory.store(
        {
            "type": "learning",
            "learning_signal": (
                first["learning"]["result"]["learning_signal"]
            )
        }
    )

    memory.store(
        {
            "type": "learning",
            "learning_signal": (
                second["learning"]["result"]["learning_signal"]
            )
        }
    )

    memories = memory.retrieve()

    assert len(memories) == 2
