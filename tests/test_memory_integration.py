from core.prediction_loop import PredictionLoop


def test_prediction_loop_stores_experience_in_memory():

    system = PredictionLoop()

    result = system.process(
        observation=10,
        actual=15
    )

    # Memory must contain the current experience
    assert result["memory"]["total_memories"] == 1

    # Memory storage must succeed
    assert result["memory"]["store"]["status"] == "stored"

    # Stored memory must contain the experience
    retrieved = result["memory"]["retrieved"]

    assert len(retrieved) == 1

    assert retrieved[0]["observation"] == 10
    assert retrieved[0]["prediction"] == 10
    assert retrieved[0]["actual"] == 15
    assert retrieved[0]["difference"] == 5


def test_memory_persists_across_multiple_cycles():

    system = PredictionLoop()

    first = system.process(
        observation=10,
        actual=15
    )

    second = system.process(
        observation=20,
        actual=25
    )

    assert first["memory"]["total_memories"] == 1
    assert second["memory"]["total_memories"] == 2

    all_memories = system.memory.retrieve_all()

    assert len(all_memories) == 2

    assert all_memories[0]["observation"] == 10
    assert all_memories[1]["observation"] == 20


def test_memory_retrieval_uses_prediction_error():

    system = PredictionLoop()

    system.process(
        observation=10,
        actual=10
    )

    system.process(
        observation=20,
        actual=25
    )

    result = system.process(
        observation=30,
        actual=35
    )

    retrieved = result["memory"]["retrieved"]

    # Current difference is 5.
    # Only memories with difference >= 5
    # should be retrieved.
    assert len(retrieved) == 2

    assert retrieved[0]["difference"] == 5
    assert retrieved[1]["difference"] == 5
