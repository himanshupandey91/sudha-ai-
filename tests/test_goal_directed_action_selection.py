from core.action import ActionEngine


def test_action_engine_selects_action_that_moves_toward_goal():
    engine = ActionEngine()

    context = {
        "current_state": {
            "temperature": 20.0
        },
        "goal": {
            "temperature": 22.0
        },
        "predicted_effects": {
            "increase_temperature": 1.0,
            "decrease_temperature": -1.0
        },
        "available_actions": [
            "increase_temperature",
            "decrease_temperature"
        ]
    }

    result = engine.select_action(context)

    assert result["status"] == "selected"
    assert result["action"] == "increase_temperature"


def test_action_selection_rejects_invalid_context():
    engine = ActionEngine()

    result = engine.select_action(None)

    assert result["status"] == "rejected"
    assert result["reason"] == "context_must_be_a_dict"
