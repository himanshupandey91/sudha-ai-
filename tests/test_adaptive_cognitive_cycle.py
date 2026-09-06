"""
Tests for Sudha AI Adaptive Cognitive Cycle.
"""

from core.adaptive_cognitive_cycle import AdaptiveCognitiveCycle


class FakeCognitiveExperiment:

    def __init__(self):
        self.calls = []

    def reason(self, goal, context):
        self.calls.append(
            {
                "goal": goal,
                "context": context
            }
        )

        return {
            "status": "ready",
            "goal": goal.get("goal"),
            "context": context
        }


def test_initial_configuration():
    engine = AdaptiveCognitiveCycle(
        cognitive_experiment=FakeCognitiveExperiment(),
        max_cycles=3
    )

    config = engine.get_configuration()

    assert config["cognitive_experiment"] == "FakeCognitiveExperiment"
    assert config["max_cycles"] == 3
    assert config["stopped"] is False
    assert config["history_size"] == 0


def test_run_single_cycle():
    experiment = FakeCognitiveExperiment()

    engine = AdaptiveCognitiveCycle(
        cognitive_experiment=experiment,
        max_cycles=3
    )

    result = engine.run_cycle(
        goal={"goal": "test"},
        context={"value": 10}
    )

    assert result["status"] == "ready"
    assert result["goal"] == "test"
    assert result["context"]["value"] == 10
    assert len(experiment.calls) == 1


def test_run_multiple_cycles():
    experiment = FakeCognitiveExperiment()

    engine = AdaptiveCognitiveCycle(
        cognitive_experiment=experiment,
        max_cycles=3
    )

    result = engine.run(
        goal={"goal": "learn"},
        context={"value": 5}
    )

    assert result["status"] == "completed"
    assert result["cycles_completed"] == 3
    assert result["max_cycles"] == 3
    assert len(result["results"]) == 3
    assert len(experiment.calls) == 3


def test_history_records_cycles():
    experiment = FakeCognitiveExperiment()

    engine = AdaptiveCognitiveCycle(
        cognitive_experiment=experiment,
        max_cycles=2
    )

    engine.run(
        goal={"goal": "memory"},
        context={"value": 7}
    )

    history = engine.get_history()

    assert len(history) == 2
    assert history[0]["status"] == "ready"
    assert history[1]["status"] == "ready"


def test_stop_prevents_cycle():
    experiment = FakeCognitiveExperiment()

    engine = AdaptiveCognitiveCycle(
        cognitive_experiment=experiment,
        max_cycles=5
    )

    engine.stop()

    result = engine.run_cycle(
        goal={"goal": "test"},
        context={}
    )

    assert result["status"] == "stopped"
    assert result["reason"] == "stop_requested"
    assert len(experiment.calls) == 0


def test_reset_allows_cycle_again():
    experiment = FakeCognitiveExperiment()

    engine = AdaptiveCognitiveCycle(
        cognitive_experiment=experiment,
        max_cycles=2
    )

    engine.stop()

    assert engine.is_stopped() is True

    engine.reset()

    assert engine.is_stopped() is False

    result = engine.run_cycle(
        goal={"goal": "test"},
        context={}
    )

    assert result["status"] == "ready"
    assert len(experiment.calls) == 1


def test_missing_experiment_is_safe():
    engine = AdaptiveCognitiveCycle(
        cognitive_experiment=None,
        max_cycles=2
    )

    result = engine.run_cycle(
        goal={"goal": "test"},
        context={}
    )

    assert result["status"] == "unavailable"
    assert result["reason"] == "cognitive_experiment_not_configured"


def test_invalid_experiment_result_is_safe():
    class InvalidExperiment:

        def reason(self, goal, context):
            return "invalid"

    engine = AdaptiveCognitiveCycle(
        cognitive_experiment=InvalidExperiment(),
        max_cycles=2
    )

    result = engine.run_cycle(
        goal={"goal": "test"},
        context={}
    )

    assert result["status"] == "failed"
    assert result["reason"] == "invalid_cycle_result"


def test_experiment_exception_is_safe():
    class BrokenExperiment:

        def reason(self, goal, context):
            raise RuntimeError("test error")

    engine = AdaptiveCognitiveCycle(
        cognitive_experiment=BrokenExperiment(),
        max_cycles=2
    )

    result = engine.run_cycle(
        goal={"goal": "test"},
        context={}
    )

    assert result["status"] == "failed"
    assert result["reason"] == "cognitive_experiment_error"
    assert result["error"] == "test error"


def test_clear_history():
    experiment = FakeCognitiveExperiment()

    engine = AdaptiveCognitiveCycle(
        cognitive_experiment=experiment,
        max_cycles=2
    )

    engine.run(
        goal={"goal": "test"},
        context={}
    )

    assert len(engine.get_history()) == 2

    engine.clear_history()

    assert len(engine.get_history()) == 0
    assert engine.get_configuration()["history_size"] == 0


def test_invalid_max_cycles():
    try:
        AdaptiveCognitiveCycle(
            cognitive_experiment=FakeCognitiveExperiment(),
            max_cycles=0
        )
        assert False
    except ValueError as error:
        assert str(error) == "max_cycles must be greater than zero"


def test_invalid_max_cycles_type():
    try:
        AdaptiveCognitiveCycle(
            cognitive_experiment=FakeCognitiveExperiment(),
            max_cycles="5"
        )
        assert False
    except ValueError as error:
        assert str(error) == "max_cycles must be an integer"
