from core.goal import GoalEngine


def test_goal_generation_from_prediction_error():

    engine = GoalEngine()

    state = {
        "observation": 10,
        "prediction": 10,
        "actual": 15,
        "difference": 5
    }

    result = engine.generate(state)

    assert result["goal"] == "reduce_prediction_error"
    assert result["priority"] == 5
