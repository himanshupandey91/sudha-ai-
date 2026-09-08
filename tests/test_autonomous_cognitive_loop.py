"""
Tests for Sudha AI Autonomous Cognitive Loop.
"""

import pytest

from core.autonomous_cognitive_loop import (
    AutonomousCognitiveLoop
)
from core.cognitive_experiment import (
    CognitiveExperimentEngine
)


class DeterministicSequenceExperiment:

    def __init__(self, results):
        self.results = list(results)
        self.calls = []

    def run(
        self,
        observation,
        hypothesis=None
    ):
        self.calls.append(
            {
                "observation": observation,
                "hypothesis": hypothesis
            }
        )

        if not self.results:
            raise RuntimeError(
                "no_more_results"
            )

        return self.results.pop(0)


def create_loop(results):
    engine = CognitiveExperimentEngine()

    experiment = (
        DeterministicSequenceExperiment(
            results
        )
    )

    engine.experiment_loop.experiment = (
        experiment
    )

    loop = AutonomousCognitiveLoop(
        engine
    )

    return loop, engine, experiment


def test_autonomous_loop_runs_multiple_cycles():
    loop, engine, experiment = create_loop(
        [
            20,
            10,
            20
        ]
    )

    result = loop.run(
        {
            "goal": "reduce_prediction_error"
        },
        [
            10,
            10,
            10
        ],
        max_cycles=3
    )

    assert result["status"] == "completed"
    assert result["cycle_count"] == 3
    assert result["reason"] == (
        "max_cycles_reached"
    )

    assert len(result["cycles"]) == 3

    assert result["cycles"][0]["prediction"] == 10
    assert result["cycles"][0]["actual"] == 20
    assert result["cycles"][0]["difference"] == 10

    assert result["cycles"][1]["prediction"] == 15
    assert result["cycles"][1]["actual"] == 10
    assert result["cycles"][1]["difference"] == 5

    assert result["cycles"][2]["prediction"] == 12.5
    assert result["cycles"][2]["actual"] == 20
    assert result["cycles"][2]["difference"] == 7.5

    assert engine.get_cycle_count() == 3
    assert len(experiment.calls) == 3


def test_autonomous_loop_respects_hard_cycle_limit():
    loop, engine, experiment = create_loop(
        [
            20,
            10,
            20,
            10,
            20
        ]
    )

    result = loop.run(
        {
            "goal": "reduce_prediction_error"
        },
        [
            10,
            10,
            10,
            10,
            10
        ],
        max_cycles=2
    )

    assert result["status"] == "completed"
    assert result["cycle_count"] == 2
    assert result["reason"] == (
        "max_cycles_reached"
    )

    assert len(result["cycles"]) == 2
    assert len(experiment.calls) == 2
    assert engine.get_cycle_count() == 2


def test_autonomous_loop_stops_when_observations_end():
    loop, engine, experiment = create_loop(
        [
            20,
            10
        ]
    )

    result = loop.run(
        {
            "goal": "reduce_prediction_error"
        },
        [
            10,
            10
        ],
        max_cycles=5
    )

    assert result["status"] == "completed"
    assert result["cycle_count"] == 2
    assert result["reason"] == (
        "observations_exhausted"
    )

    assert len(result["cycles"]) == 2
    assert len(experiment.calls) == 2
    assert engine.get_cycle_count() == 2


def test_autonomous_loop_does_not_invent_actual_results():
    loop, engine, experiment = create_loop(
        [
            20
        ]
    )

    result = loop.run(
        {
            "goal": "reduce_prediction_error"
        },
        [
            10
        ],
        max_cycles=1
    )

    assert result["status"] == "completed"

    cycle = result["cycles"][0]

    assert cycle["actual"] == 20
    assert cycle["actual"] != cycle["observation"]


def test_autonomous_loop_uses_real_learning_between_cycles():
    loop, engine, experiment = create_loop(
        [
            20,
            10,
            20
        ]
    )

    result = loop.run(
        {
            "goal": "reduce_prediction_error"
        },
        [
            10,
            10,
            10
        ],
        max_cycles=3
    )

    predictions = [
        cycle["prediction"]
        for cycle in result["cycles"]
    ]

    assert predictions == [
        10,
        15,
        12.5
    ]

    learned = (
        engine.get_learned_hypotheses()
    )

    assert len(learned) >= 1

    selected = None

    for record in learned:
        if record["hypothesis"] == (
            "use_recent_experience"
        ):
            selected = record
            break

    assert selected is not None

    assert selected["attempts"] == 3

    assert selected["average_error"] == (
        (10 + 5 + 7.5) / 3
    )


def test_autonomous_loop_can_be_stopped():
    loop, engine, experiment = create_loop(
        [
            20,
            10,
            20
        ]
    )

    engine.stop()

    result = loop.run(
        {
            "goal": "reduce_prediction_error"
        },
        [
            10,
            10,
            10
        ],
        max_cycles=3
    )

    assert result["status"] == "stopped"
    assert result["reason"] == (
        "cognitive_engine_stopped"
    )
    assert result["cycle_count"] == 0
    assert len(experiment.calls) == 0


def test_autonomous_loop_requires_goal():
    loop, _, _ = create_loop(
        [20]
    )

    with pytest.raises(
        ValueError,
        match="goal_state must contain a goal"
    ):
        loop.run(
            {},
            [10],
            max_cycles=1
        )


def test_autonomous_loop_requires_observation_sequence():
    loop, _, _ = create_loop(
        [20]
    )

    with pytest.raises(
        TypeError,
        match="observations must be a list or tuple"
    ):
        loop.run(
            {
                "goal": "reduce_prediction_error"
            },
            10,
            max_cycles=1
        )


def test_autonomous_loop_requires_positive_max_cycles():
    loop, _, _ = create_loop(
        [20]
    )

    with pytest.raises(
        ValueError,
        match="max_cycles must be greater than zero"
    ):
        loop.run(
            {
                "goal": "reduce_prediction_error"
            },
            [10],
            max_cycles=0
        )


def test_autonomous_loop_rejects_boolean_max_cycles():
    loop, _, _ = create_loop(
        [20]
    )

    with pytest.raises(
        TypeError,
        match="max_cycles must be an integer"
    ):
        loop.run(
            {
                "goal": "reduce_prediction_error"
            },
            [10],
            max_cycles=True
        )
