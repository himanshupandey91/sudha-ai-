from core.learning import LearningEngine


def test_learning_engine():

    engine = LearningEngine()

    result = engine.learn(5)

    assert result["error"] == 5
    assert result["learning_signal"] == 5
