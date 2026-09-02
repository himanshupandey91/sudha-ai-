from core.planning import PlanningEngine


def test_planning_from_prediction_error_goal():

    engine = PlanningEngine()

    goal_state = {
        "goal": "reduce_prediction_error",
        "priority": 5
    }

    result = engine.create_plan(goal_state)

    assert result["goal"] == "reduce_prediction_error"

    assert result["plan"] == [
        "observe_new_data",
        "make_new_prediction",
        "compare_prediction_with_actual"
    ]
