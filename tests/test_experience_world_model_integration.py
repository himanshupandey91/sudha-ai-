from core.experience_learning import ExperienceLearningEngine
from core.world_model import WorldModel


def test_experience_learning_updates_world_model():
    world_model = WorldModel()

    engine = ExperienceLearningEngine(
        world_model=world_model
    )

    result = engine.run(
        observation=10,
        actual=15
    )

    assert result["status"] == "completed"

    assert result["prediction"] == 10
    assert result["actual"] == 15
    assert result["difference"] == 5

    assert "world_model" in result

    state = engine.get_world_state()

    assert state["observation"] == 10
    assert state["prediction"] == 10
    assert state["actual"] == 15
    assert state["difference"] == 5
    assert state["learning"]["error"] == 5
    assert state["experience_count"] == 1


def test_prediction_without_actual_does_not_update_world_model():
    world_model = WorldModel()

    engine = ExperienceLearningEngine(
        world_model=world_model
    )

    result = engine.run(
        observation=20
    )

    assert result["status"] == "predicted"

    assert engine.get_experience_count() == 0

    state = engine.get_world_state()

    assert state["experience_count"] == 0
    assert state["observation"] is None


def test_multiple_experiences_update_world_model_history():
    world_model = WorldModel()

    engine = ExperienceLearningEngine(
        world_model=world_model
    )

    first = engine.run(
        observation=10,
        actual=15
    )

    second = engine.run(
        observation=20,
        actual=25
    )

    assert first["status"] == "completed"
    assert second["status"] == "completed"

    assert engine.get_experience_count() == 2

    history = engine.get_world_history()

    assert len(history) == 2

    assert history[0]["observation"] == 10
    assert history[0]["actual"] == 15

    assert history[1]["observation"] == 20
    assert history[1]["actual"] == 25


def test_world_model_learning_matches_learning_engine():
    world_model = WorldModel()

    engine = ExperienceLearningEngine(
        world_model=world_model
    )

    result = engine.run(
        observation=100,
        actual=120
    )

    state = engine.get_world_state()

    assert result["difference"] == 20

    assert state["learning"]["error"] == 20
    assert state["learning"]["learning_signal"] == 20


def test_clear_memory_resets_world_model():
    world_model = WorldModel()

    engine = ExperienceLearningEngine(
        world_model=world_model
    )

    engine.run(
        observation=10,
        actual=15
    )

    assert engine.get_memory_size() == 1
    assert engine.get_experience_count() == 1

    result = engine.clear_memory()

    assert result["status"] == "cleared"

    assert engine.get_memory_size() == 0
    assert engine.get_experience_count() == 0

    state = engine.get_world_state()

    assert state["experience_count"] == 0
    assert state["observation"] is None
    assert state["prediction"] is None
    assert state["actual"] is None
