from core.world_model import WorldModel


def test_world_model_update():

    model = WorldModel()

    state = model.update(
        observation=10,
        prediction=10,
        actual=15,
        difference=5
    )

    assert state["observation"] == 10
    assert state["prediction"] == 10
    assert state["actual"] == 15
    assert state["difference"] == 5

    assert len(model.get_history()) == 1
