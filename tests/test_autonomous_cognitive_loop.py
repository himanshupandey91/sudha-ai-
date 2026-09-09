"""
Integration tests for the autonomous cognitive loop.

These tests verify the real data-flow contract:

ObservationProvider
    -> CognitiveExperimentEngine
    -> Prediction
    -> Experiment
    -> Actual
    -> Prediction Error
    -> Learning
    -> Next Prediction
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

    The experiment returns the supplied observation as the
    actual observed result.

    This is deliberately deterministic so the test can verify
    the causal chain without inventing an outcome inside the
    cognitive engine.
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


def create_loop():
    engine = create_engine()
    loop = AutonomousCognitiveLoop(engine)

    return loop, engine


def test_autonomous_loop_runs_multiple_provider_cycles():
    provider = SequenceObservationProvider([10, 20, 30])

    loop, engine = create_loop()

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
    assert [cycle["observation"] for cycle in history] == [
        10,
        20,
        30,
    ]


def test_provider_observation_becomes_experiment_actual():
    provider = SequenceObservationProvider([20])

    loop, engine = create_loop()

    result = loop.run(
        goal_state={"goal": "observe"},
        observation_provider=provider,
        max_cycles=1,
    )

    assert result["status"] == "completed"

    history = loop.get_history()

    assert len(history) == 1

    cycle = history[0]

    assert cycle["observation"] == 20
    assert cycle["actual"] == 20


def test_prediction_error_is_calculated_from_actual_result():
    provider = SequenceObservationProvider([20])

    loop, engine = create_loop()

    result = loop.run(
        goal_state={"goal": "reduce_prediction_error"},
        observation_provider=provider,
        max_cycles=1,
    )

    assert result["status"] == "completed"

    cycle = loop.get_history()[0]

    assert cycle["prediction"] == 20
    assert cycle["actual"] == 20
    assert cycle["difference"] == 0


def test_real_learning_changes_next_prediction():
    provider = SequenceObservationProvider([20, 10])

    loop, engine = create_loop()

    result = loop.run(
        goal_state={"goal": "reduce_prediction_error"},
        observation_provider=provider,
        max_cycles=2,
    )

    assert result["status"] == "completed"

    history = loop.get_history()

    assert len(history) == 2

    first = history[0]
    second = history[1]

    assert first["observation"] == 20
    assert first["actual"] == 20

    assert second["observation"] == 10
    assert second["actual"] == 10

    assert first["prediction"] == 20

    assert second["prediction"] != first["prediction"]


def test_actual_result_is_not_created_from_prediction():
    provider = SequenceObservationProvider([50])

    loop, engine = create_loop()

    result = loop.run(
        goal_state={"goal": "observe_real_result"},
        observation_provider=provider,
        max_cycles=1,
    )

    assert result["status"] == "completed"

    cycle = loop.get_history()[0]

    assert cycle["observation"] == 50
    assert cycle["actual"] == 50

    assert cycle["actual"] == cycle["observation"]


def test_provider_is_called_once_per_cycle():
    calls = []

    def source():
        value = len(calls) + 1
        calls.append(value)
        return value

    provider = ObservationProvider(source)

    loop, engine = create_loop()

    result = loop.run(
        goal_state={"goal": "observe"},
        observation_provider=provider,
        max_cycles=4,
    )

    assert result["status"] == "completed"
    assert result["cycles"] == 4

    assert calls == [1, 2, 3, 4]

    history = loop.get_history()

    assert [cycle["observation"] for cycle in history] == [
        1,
        2,
        3,
        4,
    ]


def test_provider_exhaustion_stops_without_inventing_observation():
    provider = SequenceObservationProvider([10, 20])

    loop, engine = create_loop()

    result = loop.run(
        goal_state={"goal": "observe"},
        observation_provider=provider,
        max_cycles=5,
    )

    assert result["status"] == "completed"
    assert result["cycles"] == 2
    assert result["reason"] == "observation_provider_exhausted"

    history = loop.get_history()

    assert [cycle["observation"] for cycle in history] == [
        10,
        20,
    ]


def test_empty_provider_produces_no_cycle():
    provider = SequenceObservationProvider([])

    loop, engine = create_loop()

    result = loop.run(
        goal_state={"goal": "observe"},
        observation_provider=provider,
        max_cycles=3,
    )

    assert result["status"] == "unavailable"
    assert result["cycles"] == 0
    assert result["reason"] == "observation_provider_exhausted"

    assert loop.get_history() == []


def test_loop_rejects_two_observation_sources():
    provider = SequenceObservationProvider([10])

    loop, engine = create_loop()

    with pytest.raises(ValueError):
        loop.run(
            goal_state={"goal": "observe"},
            observations=[10],
            observation_provider=provider,
            max_cycles=1,
        )


def test_loop_requires_observation_source():
    loop, engine = create_loop()

    with pytest.raises(ValueError):
        loop.run(
            goal_state={"goal": "observe"},
            max_cycles=1,
        )


def test_loop_requires_positive_max_cycles():
    provider = SequenceObservationProvider([10])

    loop, engine = create_loop()

    with pytest.raises(ValueError):
        loop.run(
            goal_state={"goal": "observe"},
            observation_provider=provider,
            max_cycles=0,
        )


def test_loop_rejects_boolean_max_cycles():
    provider = SequenceObservationProvider([10])

    loop, engine = create_loop()

    with pytest.raises(TypeError):
        loop.run(
            goal_state={"goal": "observe"},
            observation_provider=provider,
            max_cycles=True,
)
