from core.autonomous_cognitive_loop import AutonomousCognitiveLoop
from core.cognitive_experiment import CognitiveExperimentEngine
from core.perception_observation_provider import (
    PerceptionObservationProvider,
)


class DeterministicActualExperiment:
    """
    Controlled experiment source for integration testing.

    The observation comes from the perception provider.
    The actual result comes independently from this experiment.
    This prevents the test from accidentally proving
    observation == actual.
    """

    def __init__(self, actual_results):
        self._actual_results = list(actual_results)
        self._index = 0

    def run(self, observation, hypothesis=None):
        if self._index >= len(self._actual_results):
            raise StopIteration("no more actual results")

        actual = self._actual_results[self._index]
        self._index += 1

        return {
            "status": "experiment_completed",
            "observation": observation,
            "actual": actual,
            "hypothesis": hypothesis,
        }


def create_engine(actual_results):
    engine = CognitiveExperimentEngine()

    experiment = DeterministicActualExperiment(
        actual_results
    )

    engine.experiment_loop.experiment = experiment

    return engine


def test_perception_observation_reaches_cognitive_engine():
    source_calls = []

    def source():
        source_calls.append(len(source_calls))

        return {
            "text": "temperature reading"
        }

    provider = PerceptionObservationProvider(source)

    engine = create_engine([20])

    loop = AutonomousCognitiveLoop(engine)

    result = loop.run(
        goal_state={
            "goal": "evaluate observation"
        },
        observation_provider=provider,
        max_cycles=1,
    )

    assert result["status"] == "completed"
    assert result["cycles"] == 1

    assert source_calls == [0]

    history = loop.get_history()

    assert len(history) == 1

    cycle = history[0]

    assert cycle["status"] == "completed"

    assert cycle["observation"]["status"] == (
        "observation_created"
    )

    assert cycle["observation"]["modalities"] == [
        "text"
    ]

    assert cycle["observation"]["data"]["text"] == (
        "temperature reading"
    )


def test_perception_observation_is_used_by_prediction_and_learning():
    observations = [
        "first observation",
        "second observation",
    ]

    index = 0

    def source():
        nonlocal index

        value = observations[index]
        index += 1

        return {
            "text": value
        }

    provider = PerceptionObservationProvider(source)

    engine = create_engine(
        [
            20,
            10,
        ]
    )

    loop = AutonomousCognitiveLoop(engine)

    result = loop.run(
        goal_state={
            "goal": "learn from observations"
        },
        observation_provider=provider,
        max_cycles=2,
    )

    assert result["status"] == "completed"
    assert result["cycles"] == 2

    history = loop.get_history()

    assert len(history) == 2

    first = history[0]
    second = history[1]

    assert first["observation"]["data"]["text"] == (
        "first observation"
    )

    assert second["observation"]["data"]["text"] == (
        "second observation"
    )

    assert first["actual"] == 20
    assert second["actual"] == 10

    assert "prediction" in first
    assert "prediction" in second

    assert "difference" in first
    assert "difference" in second

    assert first["learning"] is not None
    assert second["learning"] is not None

    assert first["hypothesis_prediction_learning"][
        "status"
    ] in {
        "learned",
        "updated",
    }

    assert second["hypothesis_prediction_learning"][
        "status"
    ] in {
        "learned",
        "updated",
    }


def test_perception_does_not_replace_or_invent_observation_data():
    raw_inputs = [
        {
            "text": "alpha",
            "voice": b"voice-alpha",
        },
        {
            "text": "beta",
            "image": b"image-beta",
        },
    ]

    index = 0

    def source():
        nonlocal index

        value = raw_inputs[index]
        index += 1

        return value

    provider = PerceptionObservationProvider(source)

    engine = create_engine(
        [
            100,
            200,
        ]
    )

    loop = AutonomousCognitiveLoop(engine)

    result = loop.run(
        goal_state={
            "goal": "preserve multimodal observations"
        },
        observation_provider=provider,
        max_cycles=2,
    )

    assert result["status"] == "completed"

    history = loop.get_history()

    first_observation = history[0]["observation"]
    second_observation = history[1]["observation"]

    assert first_observation["data"] == {
        "text": "alpha",
        "voice": b"voice-alpha",
    }

    assert second_observation["data"] == {
        "text": "beta",
        "image": b"image-beta",
    }

    assert first_observation["modalities"] == [
        "text",
        "voice",
    ]

    assert second_observation["modalities"] == [
        "text",
        "image",
    ]

    assert history[0]["actual"] == 100
    assert history[1]["actual"] == 200
