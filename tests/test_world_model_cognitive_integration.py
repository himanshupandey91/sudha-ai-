from core.cognitive_experiment import CognitiveExperimentEngine
from core.world_model import WorldModel


def build_numeric_predictions():
    return {
        "collect_more_information": 10.0,
        "collect_more_observations": 10.0,
        "use_recent_experience": 10.0,
        "increase_observation_frequency": 10.0,
        "change_prediction_strategy": 10.0,
    }


def test_world_model_records_cognitive_experience():
    world_model = WorldModel()

    engine = CognitiveExperimentEngine()

    observation = 20.0

    result = engine.run_cycle(
        goal_state="reduce_prediction_error",
        observation=observation,
    )

    assert result["status"] == "completed"

    state = result["world_model"]

    assert state["observation"] == observation
    assert "prediction" in state
    assert "actual" in state
    assert "difference" in state


def test_world_model_preserves_explicit_state_transition():
    world_model = WorldModel()

    before_state = {
        "machine": "OFF",
        "temperature": 20,
    }

    after_state = {
        "machine": "ON",
        "temperature": 25,
    }

    result = world_model.record_transition(
        action={
            "type": "switch_on"
        },
        before_state=before_state,
        after_state=after_state,
    )

    assert result["status"] == "recorded"

    transition = result["transition"]

    assert transition["action"] == {
        "type": "switch_on"
    }

    assert transition["before"] == before_state
    assert transition["after"] == after_state

    assert transition["changed"]["machine"]["before"] == "OFF"
    assert transition["changed"]["machine"]["after"] == "ON"

    assert transition["changed"]["temperature"]["before"] == 20
    assert transition["changed"]["temperature"]["after"] == 25


def test_next_state_is_the_observed_after_state():
    world_model = WorldModel()

    first_state = {
        "machine": "OFF",
        "temperature": 20,
    }

    second_state = {
        "machine": "ON",
        "temperature": 25,
    }

    world_model.update_world_state(first_state)

    assert world_model.get_world_state() == first_state

    result = world_model.record_transition(
        action={
            "type": "switch_on"
        },
        before_state=first_state,
        after_state=second_state,
    )

    assert result["status"] == "recorded"

    next_state = world_model.get_world_state()

    assert next_state == second_state
    assert next_state["machine"] == "ON"
    assert next_state["temperature"] == 25
