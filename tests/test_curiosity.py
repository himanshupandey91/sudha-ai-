from core.curiosity import CuriosityEngine


def test_curiosity_engine():

    engine = CuriosityEngine()

    result = engine.calculate(5)

    assert result["difference"] == 5
    assert result["curiosity"] == 5
