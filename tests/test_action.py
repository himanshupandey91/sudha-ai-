from core.action import ActionEngine


def test_allowed_action_is_executed():

    engine = ActionEngine()

    result = engine.execute("observe_new_data")

    assert result["action"] == "observe_new_data"
    assert result["status"] == "ready"


def test_unknown_action_is_rejected():

    engine = ActionEngine()

    result = engine.execute("unknown_action")

    assert result["action"] == "unknown_action"
    assert result["status"] == "rejected"
    assert result["reason"] == "action_not_allowed"


def test_valid_plan_is_executed():

    engine = ActionEngine()

    plan = [
        "observe_new_data",
        "make_new_prediction",
        "compare_prediction_with_actual"
    ]

    result = engine.execute_plan(plan)

    assert result["status"] == "completed"
    assert len(result["results"]) == 3

    assert result["results"][0]["action"] == "observe_new_data"
    assert result["results"][0]["status"] == "ready"

    assert result["results"][1]["action"] == "make_new_prediction"
    assert result["results"][1]["status"] == "ready"

    assert result["results"][2]["action"] == "compare_prediction_with_actual"
    assert result["results"][2]["status"] == "ready"


def test_invalid_action_stops_plan():

    engine = ActionEngine()

    plan = [
        "observe_new_data",
        "invalid_action",
        "make_new_prediction"
    ]

    result = engine.execute_plan(plan)

    assert result["status"] == "rejected"
    assert result["reason"] == "plan_contains_invalid_action"

    assert len(result["results"]) == 2

    assert result["results"][0]["action"] == "observe_new_data"
    assert result["results"][0]["status"] == "ready"

    assert result["results"][1]["action"] == "invalid_action"
    assert result["results"][1]["status"] == "rejected"


def test_invalid_plan_type_is_rejected():

    engine = ActionEngine()

    result = engine.execute_plan("not_a_list")

    assert result["status"] == "rejected"
    assert result["reason"] == "plan_must_be_a_list"
    assert result["results"] == []
