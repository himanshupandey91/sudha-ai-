from core.prediction_loop import PredictionLoop


def test_prediction_loop_executes_planned_actions():

    system = PredictionLoop()

    result = system.process(
        observation=10,
        actual=15
    )

    # Action system must complete the planned actions
    assert result["action"]["status"] == "completed"

    # Three actions were planned and executed
    assert len(result["action"]["results"]) == 3

    # Action 1: observation
    assert result["action"]["results"][0]["action"] == "observe_new_data"
    assert result["action"]["results"][0]["status"] == "completed"
    assert result["action"]["results"][0]["observation"] == 10

    # Action 2: prediction
    assert result["action"]["results"][1]["action"] == "make_new_prediction"
    assert result["action"]["results"][1]["status"] == "completed"
    assert result["action"]["results"][1]["prediction"] == 10

    # Action 3: comparison
    assert result["action"]["results"][2]["action"] == "compare_prediction_with_actual"
    assert result["action"]["results"][2]["status"] == "completed"
    assert result["action"]["results"][2]["difference"] == 5
