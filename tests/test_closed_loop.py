from core.closed_loop import ClosedLoopLearningEngine


def test_first_cycle_prediction_learning_and_difference():
    engine = ClosedLoopLearningEngine(max_cycles=10)

    result = engine.run_cycle(
        observation=10,
        actual=15
    )

    assert result["status"] == "learned"
    assert result["cycle"]["cycle"] == 1
    assert result["cycle"]["observation"] == 10
    assert result["cycle"]["prediction"] == 10
    assert result["cycle"]["actual"] == 15
    assert result["cycle"]["difference"] == 5
    assert result["stopped"] is False

    assert engine.get_cycle_count() == 1


def test_previous_experience_influences_next_prediction():
    engine = ClosedLoopLearningEngine(max_cycles=10)

    first = engine.run_cycle(
        observation=10,
        actual=15
    )

    assert first["cycle"]["prediction"] == 10
    assert first["cycle"]["difference"] == 5

    second = engine.run_cycle(
        observation=20,
        actual=25
    )

    assert second["cycle"]["prediction"] == 25
    assert second["cycle"]["actual"] == 25
    assert second["cycle"]["difference"] == 0

    assert engine.get_cycle_count() == 2


def test_max_cycle_limit_stops_loop():
    engine = ClosedLoopLearningEngine(max_cycles=2)

    first = engine.run_cycle(
        observation=10,
        actual=15
    )

    second = engine.run_cycle(
        observation=20,
        actual=25
    )

    third = engine.run_cycle(
        observation=30,
        actual=35
    )

    assert first["status"] == "learned"
    assert second["status"] == "learned"

    assert second["stopped"] is True

    assert third["status"] == "stopped"
    assert third["reason"] == "closed_loop_stopped"

    assert engine.get_cycle_count() == 2


def test_manual_stop_stops_future_cycles():
    engine = ClosedLoopLearningEngine(max_cycles=10)

    first = engine.run_cycle(
        observation=10,
        actual=15
    )

    assert first["status"] == "learned"
    assert engine.get_cycle_count() == 1

    stop_result = engine.stop()

    assert stop_result["status"] == "stopped"
    assert stop_result["cycle_count"] == 1
    assert engine.is_stopped() is True

    second = engine.run_cycle(
        observation=20,
        actual=25
    )

    assert second["status"] == "stopped"
    assert second["reason"] == "closed_loop_stopped"

    assert engine.get_cycle_count() == 1


def test_stopped_loop_cannot_predict():
    engine = ClosedLoopLearningEngine(max_cycles=10)

    engine.stop()

    result = engine.predict(100)

    assert result["status"] == "stopped"
    assert result["reason"] == "closed_loop_stopped"


def test_reset_reactivates_loop():
    engine = ClosedLoopLearningEngine(max_cycles=1)

    first = engine.run_cycle(
        observation=10,
        actual=15
    )

    assert first["status"] == "learned"
    assert engine.is_stopped() is True
    assert engine.get_cycle_count() == 1

    reset_result = engine.reset()

    assert reset_result["status"] == "reset"
    assert engine.is_stopped() is False
    assert engine.get_cycle_count() == 0
    assert engine.get_history() == []

    second = engine.run_cycle(
        observation=20,
        actual=25
    )

    assert second["status"] == "learned"
    assert second["cycle"]["cycle"] == 1
    assert engine.get_cycle_count() == 1


def test_history_contains_each_completed_cycle():
    engine = ClosedLoopLearningEngine(max_cycles=5)

    engine.run_cycle(
        observation=10,
        actual=15
    )

    engine.run_cycle(
        observation=20,
        actual=25
    )

    history = engine.get_history()

    assert len(history) == 2

    assert history[0]["cycle"] == 1
    assert history[0]["observation"] == 10
    assert history[0]["actual"] == 15
    assert history[0]["difference"] == 5

    assert history[1]["cycle"] == 2
    assert history[1]["observation"] == 20
    assert history[1]["actual"] == 25
    assert history[1]["difference"] == 0
