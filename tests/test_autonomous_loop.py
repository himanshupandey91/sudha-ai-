"""
Tests for Sudha AI AutonomousLoop
"""

import pytest

from core.autonomous_loop import AutonomousLoop
from core.closed_loop import ClosedLoopLearningEngine


class SequenceProvider:
    """Simple observation provider for tests."""

    def __init__(self, values):
        self.values = list(values)
        self.index = 0

    def observe(self):
        if self.index >= len(self.values):
            raise StopIteration("no more observations")
        value = self.values[self.index]
        self.index += 1
        return value


class ActualProvider:
    """Provides actual outcomes for given observations."""

    def __init__(self, mapping):
        self.mapping = dict(mapping)

    def get_actual(self, observation):
        return self.mapping.get(observation, observation)


def test_autonomous_loop_runs_multiple_cycles():
    engine = ClosedLoopLearningEngine(max_cycles=20)
    loop = AutonomousLoop(engine, max_cycles=3)

    provider = SequenceProvider([10, 10, 10])
    actual_provider = ActualProvider({10: 20})

    result = loop.run(
        observation_provider=provider,
        actual_provider=actual_provider,
        max_cycles=3,
    )

    assert result["status"] == "completed"
    assert result["cycles"] == 3
    assert result["reason"] == "max_cycles_reached"
    assert len(loop.get_history()) == 3


def test_autonomous_loop_stops_when_observations_end():
    engine = ClosedLoopLearningEngine(max_cycles=20)
    loop = AutonomousLoop(engine, max_cycles=10)

    provider = SequenceProvider([10, 20])

    result = loop.run(
        observation_provider=provider,
        max_cycles=10,
    )

    assert result["status"] == "completed"
    assert result["cycles"] == 2
    assert result["reason"] == "observation_provider_exhausted"


def test_autonomous_loop_respects_max_cycles():
    engine = ClosedLoopLearningEngine(max_cycles=20)
    loop = AutonomousLoop(engine, max_cycles=2)

    provider = SequenceProvider([10, 20, 30, 40, 50])

    result = loop.run(observation_provider=provider)

    assert result["status"] == "completed"
    assert result["cycles"] == 2
    assert result["reason"] == "max_cycles_reached"


def test_autonomous_loop_can_be_stopped():
    engine = ClosedLoopLearningEngine(max_cycles=20)
    loop = AutonomousLoop(engine, max_cycles=5)

    loop.stop()

    provider = SequenceProvider([10, 20, 30])
    result = loop.run(observation_provider=provider)

    assert result["status"] == "stopped"
    assert result["cycles"] == 0
    assert result["reason"] == "stopped_before_start"


def test_autonomous_loop_reset_works():
    engine = ClosedLoopLearningEngine(max_cycles=20)
    loop = AutonomousLoop(engine, max_cycles=5)

    provider = SequenceProvider([10, 20])
    loop.run(observation_provider=provider)

    assert loop.get_cycle_count() == 2

    loop.reset()

    assert loop.get_cycle_count() == 0
    assert loop.get_history() == []
    assert loop.is_stopped() is False


def test_autonomous_loop_learning_happens_across_cycles():
    """
    Check that learning from previous cycle affects next prediction.
    """
    engine = ClosedLoopLearningEngine(max_cycles=20)
    loop = AutonomousLoop(engine, max_cycles=3)

    provider = SequenceProvider([10, 10, 10])
    actual_provider = ActualProvider({10: 20})

    result = loop.run(
        observation_provider=provider,
        actual_provider=actual_provider,
        max_cycles=3,
    )

    assert result["status"] == "completed"
    history = loop.get_history()

    assert len(history) == 3

    # First cycle: prediction should be close to observation (10)
    first = history[0]
    assert first["cycle"]["observation"] == 10
    assert first["cycle"]["actual"] == 20
    assert first["cycle"]["difference"] == 10

    # Later cycles should show some adaptation
    assert history[1]["cycle"]["prediction"] != history[0]["cycle"]["prediction"] or \
           history[2]["cycle"]["prediction"] != history[0]["cycle"]["prediction"]


def test_autonomous_loop_rejects_invalid_max_cycles():
    engine = ClosedLoopLearningEngine()

    with pytest.raises(ValueError, match="max_cycles"):
        AutonomousLoop(engine, max_cycles=0)

    with pytest.raises(TypeError, match="max_cycles"):
        AutonomousLoop(engine, max_cycles=True)


def test_autonomous_loop_requires_learning_engine():
    with pytest.raises(ValueError, match="learning_engine"):
        AutonomousLoop(None)


def test_callable_observation_provider_works():
    engine = ClosedLoopLearningEngine(max_cycles=20)
    loop = AutonomousLoop(engine, max_cycles=2)

    values = [5, 15]
    index = {"i": 0}

    def provider():
        if index["i"] >= len(values):
            raise StopIteration
        val = values[index["i"]]
        index["i"] += 1
        return val

    result = loop.run(observation_provider=provider, max_cycles=2)

    assert result["status"] == "completed"
    assert result["cycles"] == 2
