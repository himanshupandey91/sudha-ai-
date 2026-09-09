"""
Regression tests for Sudha AI Autonomous Cognitive Loop.

These tests preserve coverage for the original autonomous-loop behaviors
while matching the current observation/provider API.

The tests intentionally separate:
    observation
from:
    actual experiment result

This prevents a zero-error first cycle from being incorrectly interpreted
as evidence that learning must change the next prediction.
"""

import pytest

from core.autonomous_cognitive_loop import AutonomousCognitiveLoop
from core.cognitive_experiment import CognitiveExperimentEngine
from core.observation_provider import SequenceObservationProvider


class DeterministicSequenceExperiment:
    """
    Controlled experiment used to verify deterministic data flow.

    The observation is the input to the experiment.
    The returned result is the externally supplied actual outcome.

    Keeping these two values separate allows the tests to verify that
    the cognitive loop does not manufacture the actual result from
    its prediction.
    """

    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def run(self, observation, hypothesis=None):
        self.calls.append(
            {
                "observation": observation,
                "hypothesis": hypothesis,
            }
        )

        if not self.results:
            raise RuntimeError("no_more_results")

        return self.results.pop(0)


def create_loop(results):
    """
    Create a cognitive engine with a deterministic experiment.
    """
    engine = CognitiveExperimentEngine()
    experiment = DeterministicSequenceExperiment(results)

    engine.experiment_loop.experiment = experiment

    loop = AutonomousCognitiveLoop(engine)

    return loop, engine, experiment


def test_autonomous_loop_runs_multiple_cycles():
    loop, engine, experiment = create_loop(
        [20, 10, 20]
    )

    result = loop.run(
        {
            "goal": "reduce_prediction_error",
        },
        observations=[
            10,
            10,
            10,
        ],
        max_cycles=3,
    )

    assert result["status"] == "completed"
    assert result["cycle_count"] == 3
    assert result["cycles"] == 3
    assert result["reason"] == "max_cycles_reached"

    history = loop.get_history()

    assert len(history) == 3

    assert history[0]["prediction"] == 10
    assert history[0]["actual"] == 20
    assert history[0]["difference"] == 10

    assert history[1]["prediction"] == 15
    assert history[1]["actual"] == 10
    assert history[1]["difference"] == 5

    assert history[2]["prediction"] == 12.5
    assert history[2]["actual"] == 20
    assert history[2]["difference"] == 7.5

    assert engine.get_cycle_count() == 3
    assert len(experiment.calls) == 3


def test_autonomous_loop_respects_hard_cycle_limit():
    loop, engine, experiment = create_loop(
        [20, 10, 20, 10, 20]
    )

    result = loop.run(
        {
            "goal": "reduce_prediction_error",
        },
        observations=[
            10,
            10,
            10,
            10,
            10,
        ],
        max_cycles=2,
    )

    assert result["status"] == "completed"
    assert result["cycle_count"] == 2
    assert result["cycles"] == 2
    assert result["reason"] == "max_cycles_reached"

    assert len(loop.get_history()) == 2
    assert len(experiment.calls) == 2
    assert engine.get_cycle_count() == 2


def test_autonomous_loop_stops_when_observations_end():
    loop, engine, experiment = create_loop(
        [20, 10]
    )

    result = loop.run(
        {
            "goal": "reduce_prediction_error",
        },
        observations=[
            10,
            10,
        ],
        max_cycles=5,
    )

    assert result["status"] == "completed"
    assert result["cycle_count"] == 2
    assert result["cycles"] == 2
    assert result["reason"] == "observations_exhausted"

    assert len(loop.get_history()) == 2
    assert len(experiment.calls) == 2
    assert engine.get_cycle_count() == 2


def test_autonomous_loop_does_not_invent_actual_results():
    loop, _, _ = create_loop(
        [20]
    )

    result = loop.run(
        {
            "goal": "reduce_prediction_error",
        },
        observations=[
            10,
        ],
        max_cycles=1,
    )

    assert result["status"] == "completed"

    cycle = loop.get_history()[0]

    assert cycle["actual"] == 20
    assert cycle["actual"] != cycle["observation"]


def test_autonomous_loop_uses_real_learning_between_cycles():
    """
    Verify that a real prediction error in cycle 1 changes the
    predictor state used in cycle 2.

    Observation is intentionally kept at 10 for both cycles.

    Actual experiment outcomes are:
        cycle 1 -> 20
        cycle 2 -> 10

    Therefore the first cycle has a non-zero error and learning
    should affect the next prediction.
    """

    loop, engine, _ = create_loop(
        [20, 10, 20]
    )

    result = loop.run(
        {
            "goal": "reduce_prediction_error",
        },
        observations=[
            10,
            10,
            10,
        ],
        max_cycles=3,
    )

    assert result["status"] == "completed"

    predictions = [
        cycle["prediction"]
        for cycle in loop.get_history()
    ]

    assert predictions == [
        10,
        15,
        12.5,
    ]

    learned = engine.get_learned_hypotheses()

    assert len(learned) >= 1

    selected = None

    for record in learned:
        if record["hypothesis"] == "use_recent_experience":
            selected = record
            break

    assert selected is not None
    assert selected["attempts"] == 3
    assert selected["average_error"] == (
        (10 + 5 + 7.5) / 3
    )


def test_autonomous_loop_can_be_stopped():
    loop, engine, experiment = create_loop(
        [20, 10, 20]
    )

    engine.stop()

    result = loop.run(
        {
            "goal": "reduce_prediction_error",
        },
        observations=[
            10,
            10,
            10,
        ],
        max_cycles=3,
    )

    assert result["status"] == "stopped"
    assert result["reason"] == "stopped"
    assert result["cycle_count"] == 0
    assert result["cycles"] == 0
    assert result["stopped"] is True
    assert len(experiment.calls) == 0


def test_autonomous_loop_requires_goal():
    loop, _, _ = create_loop(
        [20]
    )

    with pytest.raises(
        (TypeError, ValueError),
        match="goal_state",
    ):
        loop.run(
            {},
            observations=[10],
            max_cycles=1,
        )


def test_autonomous_loop_requires_observation_sequence():
    loop, _, _ = create_loop(
        [20]
    )

    with pytest.raises(
        (TypeError, ValueError),
        match="observations|observation source",
    ):
        loop.run(
            {
                "goal": "reduce_prediction_error",
            },
            observations=10,
            max_cycles=1,
        )


def test_autonomous_loop_requires_positive_max_cycles():
    loop, _, _ = create_loop(
        [20]
    )

    with pytest.raises(
        ValueError,
        match="max_cycles",
    ):
        loop.run(
            {
                "goal": "reduce_prediction_error",
            },
            observations=[10],
            max_cycles=0,
        )


def test_autonomous_loop_rejects_boolean_max_cycles():
    loop, _, _ = create_loop(
        [20]
    )

    with pytest.raises(
        TypeError,
        match="max_cycles must be an integer",
    ):
        loop.run(
            {
                "goal": "reduce_prediction_error",
            },
            observations=[10],
            max_cycles=True,
        )


def test_autonomous_loop_preserves_observation_provider_compatibility():
    provider = SequenceObservationProvider(
        [10, 20, 30]
    )

    loop, _, _ = create_loop(
        [10, 20, 30]
    )

    result = loop.run(
        {
            "goal": "observe",
        },
        observation_provider=provider,
        max_cycles=3,
    )

    assert result["status"] == "completed"
    assert result["cycle_count"] == 3
    assert result["cycles"] == 3
    assert result["reason"] == "max_cycles_reached"

    history = loop.get_history()

    assert len(history) == 3

    assert [
        item["observation"]
        for item in history
    ] == [
        10,
        20,
        30,
    ]


def test_provider_learning_changes_prediction():
    """
    Verify the complete provider -> prediction -> actual -> learning
    -> next prediction chain.

    Provider observations:
        [10, 10]

    Actual experiment outcomes:
        [20, 10]

    Expected:
        Cycle 1:
            prediction = 10
            actual = 20
            error = 10

        Learning:
            prediction becomes 15

        Cycle 2:
            prediction = 15
            actual = 10
            error = 5
    """

    provider = SequenceObservationProvider(
        [10, 10]
    )

    loop, engine, experiment = create_loop(
        [20, 10]
    )

    result = loop.run(
        {
            "goal": "reduce_prediction_error",
        },
        observation_provider=provider,
        max_cycles=2,
    )

    assert result["status"] == "completed"

    history = loop.get_history()

    assert len(history) == 2

    first = history[0]
    second = history[1]

    assert first["observation"] == 10
    assert first["prediction"] == 10
    assert first["actual"] == 20
    assert first["difference"] == 10

    assert second["observation"] == 10
    assert second["prediction"] == 15
    assert second["actual"] == 10
    assert second["difference"] == 5

    assert second["prediction"] != first["prediction"]

    assert len(experiment.calls) == 2
    assert engine.get_cycle_count() == 2
