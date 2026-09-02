from core.memory import MemoryEngine


def test_memory_stores_experience():

    memory = MemoryEngine()

    result = memory.store({
        "observation": 10,
        "prediction": 10,
        "actual": 15,
        "difference": 5
    })

    assert result["status"] == "stored"
    assert result["memory_size"] == 1
    assert memory.size() == 1


def test_memory_retrieves_experiences():

    memory = MemoryEngine()

    experience = {
        "observation": 10,
        "prediction": 10,
        "actual": 15,
        "difference": 5
    }

    memory.store(experience)

    result = memory.retrieve_all()

    assert len(result) == 1
    assert result[0]["observation"] == 10
    assert result[0]["difference"] == 5


def test_memory_retrieves_recent_experiences():

    memory = MemoryEngine()

    memory.store({"observation": 1})
    memory.store({"observation": 2})
    memory.store({"observation": 3})

    result = memory.retrieve_recent(2)

    assert len(result) == 2
    assert result[0]["observation"] == 2
    assert result[1]["observation"] == 3


def test_memory_retrieves_high_error_experiences():

    memory = MemoryEngine()

    memory.store({
        "observation": 10,
        "difference": 2
    })

    memory.store({
        "observation": 20,
        "difference": 8
    })

    memory.store({
        "observation": 30,
        "difference": 5
    })

    result = memory.retrieve_by_difference(5)

    assert len(result) == 2
    assert result[0]["difference"] == 8
    assert result[1]["difference"] == 5


def test_memory_limit_removes_oldest_memory():

    memory = MemoryEngine(max_memories=2)

    memory.store({"observation": 1})
    memory.store({"observation": 2})
    memory.store({"observation": 3})

    result = memory.retrieve_all()

    assert len(result) == 2
    assert result[0]["observation"] == 2
    assert result[1]["observation"] == 3


def test_memory_clear():

    memory = MemoryEngine()

    memory.store({"observation": 10})
    memory.store({"observation": 20})

    result = memory.clear()

    assert result["status"] == "cleared"
    assert result["memory_size"] == 0
    assert memory.size() == 0
