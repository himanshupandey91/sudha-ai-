from core.adaptive_predictor import AdaptivePredictor
from core.closed_loop import ClosedLoopLearningEngine
from core.cognitive_experiment import CognitiveExperimentEngine
from core.environment import Environment
from core.executive_reasoning import ExecutiveReasoningEngine
from core.experiment_loop import ExperimentLoopEngine
from core.experience_learning import ExperienceLearningEngine
from core.hypothesis_planner import HypothesisPlanningEngine
from core.prediction import PredictionEngine
from core.world_model import WorldModel


def test_world_model_records_cognitive_experience():
    world_model = WorldModel()
    environment = Environment()

    adaptive_predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    prediction_engine = PredictionEngine(
        adaptive_predictor=adaptive_predictor
    )

    experience_learning = ExperienceLearningEngine(
        world_model=world_model
    )

    closed_loop = ClosedLoopLearningEngine(
        experience_learning=experience_learning,
        prediction_engine=prediction_engine
    )

    experiment_loop = ExperimentLoopEngine(
        closed_loop=closed_loop,
        environment=environment,
        action="increase_temperature"
    )

    hypothesis_planner = HypothesisPlanningEngine(
        exploration=True
    )

    executive_reasoning = ExecutiveReasoningEngine(
        exploration=True
    )

    engine = CognitiveExperimentEngine(
        hypothesis_planner=hypothesis_planner,
        experiment_loop=experiment_loop,
        executive_reasoning=executive_reasoning,
        world_model=world_model
    )

    observation = environment.get_state()["temperature"]

    result = engine.run_cycle(
        goal_state={
            "goal": "reduce_prediction_error"
        },
        observation=observation
    )

    assert result["status"] == "completed"

    assert result["observation"] == 20.0
    assert result["actual"] == 21.0
    assert result["difference"] == 1.0

    state = result["world_model"]

    assert state["observation"] == 20.0
    assert "prediction" in state
    assert state["actual"] == 21.0
    assert state["difference"] == 1.0

    assert world_model.get_state()["actual"] == 21.0
    assert world_model.get_experience_count() == 1


def test_preserves_explicit_state_transition():
    world_model = WorldModel()

    before_state = {
        "machine": "OFF",
        "temperature": 20
    }

    after_state = {
        "machine": "ON",
        "temperature": 25
    }

    result = world_model.record_transition(
        action={
            "type": "switch_on"
        },
        before_state=before_state,
        after_state=after_state
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
        "temperature": 20
    }

    second_state = {
        "machine": "ON",
        "temperature": 25
    }

    world_model.update_world_state(first_state)

    assert world_model.get_world_state() == first_state

    result = world_model.record_transition(
        action={
            "type": "switch_on"
        },
        before_state=first_state,
        after_state=second_state
    )

    assert result["status"] == "recorded"

    next_state = world_model.get_world_state()

    assert next_state == second_state
    assert next_state["machine"] == "ON"
    assert next_state["temperature"] == 25
