from core.hierarchical_memory import HierarchicalMemory


def test_hierarchical_memory_creation():

    memory = HierarchicalMemory()

    assert memory.size() == 0


def test_working_memory_stores_data():

    memory = HierarchicalMemory()

    result = memory.store_working({
        "context": "current task",
        "value": 10,
    })

    assert result["status"] == "stored"
    assert memory.size("working") == 1

    stored = memory.retrieve_working()

    assert stored[0]["context"] == "current task"
    assert stored[0]["value"] == 10


def test_episodic_memory_stores_experience():

    memory = HierarchicalMemory()

    result = memory.store_episodic({
        "observation": 10,
        "prediction": 12,
        "actual": 15,
        "difference": 3,
    })

    assert result["status"] == "stored"
    assert memory.size("episodic") == 1

    stored = memory.retrieve_episodic()

    assert stored[0]["observation"] == 10
    assert stored[0]["difference"] == 3


def test_semantic_memory_stores_knowledge():

    memory = HierarchicalMemory()

    result = memory.store_semantic({
        "concept": "gravity",
        "value": "attraction",
    })

    assert result["status"] == "stored"
    assert memory.size("semantic") == 1

    stored = memory.retrieve_semantic()

    assert stored[0]["concept"] == "gravity"


def test_procedural_memory_stores_procedure():

    memory = HierarchicalMemory()

    result = memory.store_procedural({
        "goal": "calculate",
        "steps": ["observe", "compute"],
    })

    assert result["status"] == "stored"
    assert memory.size("procedural") == 1

    stored = memory.retrieve_procedural()

    assert stored[0]["goal"] == "calculate"


def test_memory_types_are_separated():

    memory = HierarchicalMemory()

    memory.store_working({
        "value": "working",
    })

    memory.store_episodic({
        "value": "episodic",
    })

    memory.store_semantic({
        "value": "semantic",
    })

    memory.store_procedural({
        "value": "procedural",
    })

    assert memory.retrieve_working()[0]["value"] == "working"
    assert memory.retrieve_episodic()[0]["value"] == "episodic"
    assert memory.retrieve_semantic()[0]["value"] == "semantic"
    assert memory.retrieve_procedural()[0]["value"] == "procedural"


def test_working_memory_is_bounded():

    memory = HierarchicalMemory(
        working_size=2
    )

    memory.store_working({"value": 1})
    memory.store_working({"value": 2})
    memory.store_working({"value": 3})

    result = memory.retrieve_working()

    assert len(result) == 2
    assert result[0]["value"] == 2
    assert result[1]["value"] == 3


def test_episodic_memory_is_bounded():

    memory = HierarchicalMemory(
        episodic_size=2
    )

    memory.store_episodic({"value": 1})
    memory.store_episodic({"value": 2})
    memory.store_episodic({"value": 3})

    result = memory.retrieve_episodic()

    assert len(result) == 2
    assert result[0]["value"] == 2
    assert result[1]["value"] == 3


def test_invalid_memory_is_rejected():

    memory = HierarchicalMemory()

    result = memory.store_semantic(
        "invalid"
    )

    assert result["status"] == "rejected"
    assert (
        result["reason"]
        == "memory_must_be_a_dictionary"
    )


def test_total_memory_size():

    memory = HierarchicalMemory()

    memory.store_working({"value": 1})
    memory.store_episodic({"value": 2})
    memory.store_semantic({"value": 3})
    memory.store_procedural({"value": 4})

    assert memory.size() == 4


def test_clear_single_memory_type():

    memory = HierarchicalMemory()

    memory.store_working({"value": 1})
    memory.store_episodic({"value": 2})

    result = memory.clear("working")

    assert result["status"] == "cleared"
    assert memory.size("working") == 0
    assert memory.size("episodic") == 1


def test_clear_all_memory():

    memory = HierarchicalMemory()

    memory.store_working({"value": 1})
    memory.store_episodic({"value": 2})
    memory.store_semantic({"value": 3})
    memory.store_procedural({"value": 4})

    result = memory.clear()

    assert result["status"] == "cleared"
    assert result["memory_size"] == 0
    assert memory.size() == 0


def test_retrieve_all_memory_types():

    memory = HierarchicalMemory()

    memory.store_working({"value": "w"})
    memory.store_episodic({"value": "e"})
    memory.store_semantic({"value": "s"})
    memory.store_procedural({"value": "p"})

    result = memory.retrieve_all()

    assert result["working"][0]["value"] == "w"
    assert result["episodic"][0]["value"] == "e"
    assert result["semantic"][0]["value"] == "s"
    assert result["procedural"][0]["value"] == "p"


def test_memory_configuration():

    memory = HierarchicalMemory(
        working_size=5,
        episodic_size=20,
        semantic_size=30,
        procedural_size=40,
    )

    configuration = memory.get_configuration()

    assert configuration["working_size"] == 5
    assert configuration["episodic_size"] == 20
    assert configuration["semantic_size"] == 30
    assert configuration["procedural_size"] == 40
    assert configuration["total_size"] == 0
