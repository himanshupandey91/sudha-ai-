from core.autonomous_cognitive_loop import AutonomousCognitiveLoop
from core.cognitive_experiment import CognitiveExperimentEngine
from core.perception_observation_provider import (
    PerceptionObservationProvider,
)


class DeterministicActualExperiment:
    """
    Controlled experiment source for integration testing.

    Observation comes from the perception provider.

    Actual result comes independently from this experiment.

    This keeps observation and actual result separate and
    prevents the test from accidentally proving:
        observation == actual
    """

    def __init__(self, actual_results):
        self._actual_results = list(actual_results)
        self._index = 0

    def run(self, observation, hypothesis=None):
        if self._index >= len(self._actual_results):
            raise StopIteration(
                "no more actual results"
            )

        actual = self._actual_results[
            self._index
        ]

        self._index += 1

        return {
            "status": "experiment_completed",
            "observation": observation,
            "actual": actual,
            "hypothesis": hypothesis,
        }


def create_engine(actual_results):
    """
    Create a cognitive experiment engine with:

        Perception observation
              ↓
        Numeric prediction
              ↓
        External actual result
              ↓
        Learning

    The numeric prediction is explicitly configured here
    because PredictionEngine requires predictions to be numeric.
    """

    engine = CognitiveExperimentEngine()

    experiment = DeterministicActualExperiment(
        actual_results
    )

    engine.experiment_loop.experiment = experiment

    prediction_engine = engine.prediction_engine

    numeric_predictions = {
        "collect_more_information": 10.0,
        "collect_more_observations": 10.0,
        "use_recent_experience": 10.0,
        "increase_observation_frequency": 10.0,
        "change_prediction_strategy": 10.0,
    }

    prediction_engine.hypothesis_predictions = dict(
        numeric_predictions
    )

    adaptive_predictor = (
        prediction_engine.adaptive_predictor
    )

    for hypothesis, prediction in (
        numeric_predictions.items()
    ):
        if (
            adaptive_predictor.predict(
                hypothesis
            )
            is None
        ):
            adaptive_predictor.set_prediction(
                hypothesis,
                prediction
            )

    return engine


def test_perception_observation_reaches_cognitive_engine():
    source_calls = []

    def source():
        source_calls.append(
            len(source_calls)
        )

        return {
            "text": "temperature reading"
        }

    provider = PerceptionObservationProvider(
        source
    )

    engine = create_engine(
        [20]
    )

    loop = AutonomousCognitiveLoop(
        engine
    )

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

    assert isinstance(
        cycle["prediction"],
        (int, float)
    )

    assert cycle["actual"] == 20


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

    provider = PerceptionObservationProvider(
        source
    )

    engine = create_engine(
        [
            20,
            10,
        ]
    )

    loop = AutonomousCognitiveLoop(
        engine
    )

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

    assert first["prediction"] == 10.0
    assert second["prediction"] == 15.0

    assert first["prediction"] != second["prediction"]

    assert "difference" in first
    assert "difference" in second

    assert first["difference"] == 10.0
    assert second["difference"] == 5.0

    assert first["learning"] is not None
    assert second["learning"] is not None

    assert first[
        "hypothesis_prediction_learning"
    ]["status"] in {
        "learned",
        "updated",
    }

    assert second[
        "hypothesis_prediction_learning"
    ]["status"] in {
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

    provider = PerceptionObservationProvider(
        source
    )

    engine = create_engine(
        [
            100,
            200,
        ]
    )

    loop = AutonomousCognitiveLoop(
        engine
    )

    result = loop.run(
        goal_state={
            "goal": "preserve multimodal observations"
        },
        observation_provider=provider,
        max_cycles=2,
    )

    assert result["status"] == "completed"

    history = loop.get_history()

    first_observation = history[0][
        "observation"
    ]

    second_observation = history[1][
        "observation"
    ]

    assert first_observation["data"] == {
        "text": "alpha",
        "voice": b"voice-alpha",
    }

    assert second_observation["data"] == {
        "text": "beta",
        "image": b"image-beta",
    }

    assert first_observation[
        "modalities"
    ] == [
        "text",
        "voice",
    ]

    assert second_observation[
        "modalities"
    ] == [
        "text",
        "image",
    ]

    assert history[0]["actual"] == 100
    assert history[1]["actual"] == 200

    assert isinstance(
        history[0]["prediction"],
        (int, float)
    )

    assert isinstance(
        history[1]["prediction"],
        (int, float)
    )
