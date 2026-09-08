"""
Tests for Sudha AI observation providers and autonomous integration.
"""

import pytest

from core.autonomous_cognitive_loop import AutonomousCognitiveLoop
from core.cognitive_experiment import CognitiveExperimentEngine
from core.observation_provider import (
    ObservationProvider,
    SequenceObservationProvider,
)


class DeterministicExperiment:
    """
    Controlled experiment used only to verify data flow.

    It returns the supplied observation as the actual result.
    """

    def run(self, observation, hypothesis=None):
        return {
            "actual": observation,
            "hypothesis": hypothesis,
        }


def create_engine():
    engine = CognitiveExperimentEngine()

    engine.experiment_loop.experiment = DeterministicExperiment()

    return engine


def test_observation_provider_calls_external_source():
    observations = iter([10, 20])

    provider = ObservationProvider(lambda: next(observations))

    assert provider.observe() == 10
    assert provider.observe() == 20


def test_observation_provider_requires_callable_source():
    with pytest.raises(TypeError):
        ObservationProvider("not_callable")


def test_sequence_provider_returns_supplied_observations():
    provider = SequenceObservationProvider([10, 20, 30])

    assert provider.observe() == 10
    assert provider.observe() == 20
    assert provider.observe() == 30


def test_sequence_provider_exhausts_without_inventing_data():
    provider = SequenceObservationProvider([10])

    assert provider.observe() == 10

    with pytest.raises(StopIteration):
        provider.observe()


def test_sequence_provider_can_reset():
    provider = SequenceObservationProvider([10, 20])

    assert provider.observe() == 10
    assert provider.observe() == 20

    provider.reset()

    assert provider.observe() == 10


def test_autonomous_loop_consumes_one_provider_observation_per_cycle():
    provider = SequenceObservationProvider([10, 20, 30])

    engine = create_engine()
    loop = AutonomousCognitiveLoop(engine)

    result = loop.run(
        goal_state={"goal": "learn"},
        observation_provider=provider,
        max_cycles=3,
    )

    assert result["status"] == "completed"
    assert result["cycles"] == 3
    assert result["reason"] == "max_cycles_reached"

    history = loop.get_history()

    assert len(history) == 3
    assert [item["observation"] for item in history] == [10, 20, 30]


def test_autonomous_loop_stops_when_provider_is_exhausted():
    provider = SequenceObservationProvider([10, 20])

    engine = create_engine()
    loop = AutonomousCognitiveLoop(engine)

    result = loop.run(
        goal_state={"goal": "learn"},
        observation_provider=provider,
        max_cycles=5,
    )

    assert result["status"] == "completed"
    assert result["cycles"] == 2
    assert result["reason"] == "observation_provider_exhausted"


def test_autonomous_loop_reports_empty_provider():
    provider = SequenceObservationProvider([])

    engine = create_engine()
    loop = AutonomousCognitiveLoop(engine)

    result = loop.run(
        goal_state={"goal": "learn"},
        observation_provider=provider,
        max_cycles=3,
    )

    assert result["status"] == "unavailable"
    assert result["cycles"] == 0
    assert result["reason"] == "observation_provider_exhausted"


def test_autonomous_loop_rejects_both_observation_sources():
    provider = SequenceObservationProvider([10])

    engine = create_engine()
    loop = AutonomousCognitiveLoop(engine)

    with pytest.raises(ValueError):
        loop.run(
            goal_state={"goal": "learn"},
            observations=[10],
            observation_provider=provider,
            max_cycles=1,
        )


def test_autonomous_loop_requires_an_observation_source():
    engine = create_engine()
    loop = AutonomousCognitiveLoop(engine)

    with pytest.raises(ValueError):
        loop.run(
            goal_state={"goal": "learn"},
            max_cycles=1,
        )


def test_provider_is_called_once_per_cycle():
    calls = []

    def source():
        value = len(calls) + 1
        calls.append(value)
        return value

    provider = ObservationProvider(source)

    engine = create_engine()
    loop = AutonomousCognitiveLoop(engine)

    result = loop.run(
        goal_state={"goal": "observe"},
        observation_provider=provider,
        max_cycles=4,
    )

    assert result["status"] == "completed"
    assert calls == [1, 2, 3, 4]


def test_old_observation_list_api_still_works():
    engine = create_engine()
    loop = AutonomousCognitiveLoop(engine)

    result = loop.run(
        goal_state={"goal": "compatibility"},
        observations=[10, 20, 30],
        max_cycles=3,
    )

    assert result["status"] == "completed"
    assert result["cycles"] == 3
    assert result["reason"] == "max_cycles_reached"
