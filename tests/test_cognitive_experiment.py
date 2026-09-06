from core.cognitive_experiment import CognitiveExperimentEngine

class FakeExperiment:
def init(self, result=15):
self.result = result

def run(self, observation):
    return self.result

class HypothesisAwareExperiment:
def init(self, result=15):
self.result = result
self.received_hypothesis = None

def run(self, observation, hypothesis=None):
    self.received_hypothesis = hypothesis
    return self.result

def test_engine_configuration():
engine = CognitiveExperimentEngine()

config = engine.get_configuration()

assert config["hypothesis_planner"] == "HypothesisPlanningEngine"
assert config["experiment_loop"] == "ExperimentLoopEngine"

def test_reasoning_returns_ready_plan():
engine = CognitiveExperimentEngine()

result = engine.reason(
    {
        "goal": "reduce_prediction_error"
    }
)

assert result["status"] == "ready"
assert result["goal"] == "reduce_prediction_error"
assert len(result["hypotheses"]) > 0
assert result["selected_hypothesis"] is not None
assert result["plan"] is not None

def test_reasoning_empty_goal():
engine = CognitiveExperimentEngine()

result = engine.reason({})

assert result["status"] == "unavailable"
assert result["reason"] == "no_hypothesis_available"

def test_predict_returns_prediction():
engine = CognitiveExperimentEngine()

result = engine.predict(10)

assert result["status"] == "predicted"
assert result["prediction"] == 10

def test_run_experiment_without_experiment():
engine = CognitiveExperimentEngine()

result = engine.run_experiment(
    observation=10
)

assert result["status"] == "unavailable"
assert result["reason"] == "experiment_not_configured"

def test_run_experiment_with_fake_experiment():
engine = CognitiveExperimentEngine()

experiment = FakeExperiment(result=15)
engine.experiment_loop.experiment = experiment

result = engine.run_experiment(
    observation=10
)

assert result["status"] == "experiment_completed"
assert result["actual"] == 15

def test_run_cycle_completes():
engine = CognitiveExperimentEngine()

experiment = FakeExperiment(result=15)
engine.experiment_loop.experiment = experiment

result = engine.run_cycle(
    {
        "goal": "reduce_prediction_error"
    },
    10
)

assert result["status"] == "completed"
assert result["prediction"] == 10
assert result["actual"] == 15
assert result["difference"] == 5

def test_world_model_receives_result():
engine = CognitiveExperimentEngine()

experiment = FakeExperiment(result=15)
engine.experiment_loop.experiment = experiment

result = engine.run_cycle(
    {
        "goal": "reduce_prediction_error"
    },
    10
)

state = result["world_model"]

assert result["status"] == "completed"
assert result["world_model"]["actual"] == 15
assert state["actual"] == 15

def test_run_cycle_records_history():
engine = CognitiveExperimentEngine()

experiment = FakeExperiment(result=15)
engine.experiment_loop.experiment = experiment

result = engine.run_cycle(
    {
        "goal": "reduce_prediction_error"
    },
    10
)

history = engine.get_history()

assert result["status"] == "completed"
assert len(history) == 1

def test_stop_prevents_cycle():
engine = CognitiveExperimentEngine()

experiment = FakeExperiment(result=15)
engine.experiment_loop.experiment = experiment

engine.stop()

result = engine.run_cycle(
    {
        "goal": "reduce_prediction_error"
    },
    10
)

assert result["status"] == "stopped"

def test_reset_allows_cycle_again():
engine = CognitiveExperimentEngine()

experiment = FakeExperiment(result=15)
engine.experiment_loop.experiment = experiment

engine.stop()
engine.reset()

result = engine.run_cycle(
    {
        "goal": "reduce_prediction_error"
    },
    10
)

assert result["status"] == "completed"

def test_is_stopped():
engine = CognitiveExperimentEngine()

assert engine.is_stopped() is False

engine.stop()

assert engine.is_stopped() is True

engine.reset()

assert engine.is_stopped() is False

def test_get_cycle_count():
engine = CognitiveExperimentEngine()

experiment = FakeExperiment(result=15)
engine.experiment_loop.experiment = experiment

assert engine.get_cycle_count() == 0

engine.run_cycle(
    {
        "goal": "reduce_prediction_error"
    },
    10
)

assert engine.get_cycle_count() == 1

def test_selected_hypothesis_reaches_experiment():
experiment = HypothesisAwareExperiment(
result=15
)

engine = CognitiveExperimentEngine()

engine.experiment_loop.experiment = experiment

result = engine.run_cycle(
    {
        "goal": "reduce_prediction_error"
    },
    10
)

assert result["status"] == "completed"

assert experiment.received_hypothesis["hypothesis"] == (
    "use_recent_experience"
)

assert experiment.received_hypothesis["priority"] == 3

assert experiment.received_hypothesis["learned"] is False

assert experiment.received_hypothesis["exploration"] is False

def test_selected_hypothesis_is_recorded():
experiment = HypothesisAwareExperiment(
result=20
)

engine = CognitiveExperimentEngine()

engine.experiment_loop.experiment = experiment

result = engine.run_cycle(
    {
        "goal": "reduce_prediction_error"
    },
    10
)

assert result["status"] == "completed"

learned = engine.get_learned_hypotheses()

assert len(learned) >= 1

selected = None

for record in learned:
    if record["hypothesis"] == "use_recent_experience":
        selected = record
        break

assert selected is not None
assert selected["attempts"] == 1
assert selected["average_error"] == 10

def test_better_learned_hypothesis_is_selected():
engine = CognitiveExperimentEngine()

planner = engine.hypothesis_planner

planner.record_result(
    "use_recent_experience",
    10
)

planner.record_result(
    "increase_observation_frequency",
    2
)

reasoning = engine.reason(
    {
        "goal": "reduce_prediction_error"
    }
)

selected = reasoning["selected_hypothesis"]

assert selected["hypothesis"] == (
    "increase_observation_frequency"
)

assert selected["learned"] is True
assert selected["average_error"] == 2
assert selected["attempts"] == 1
assert selected["score"] == 1 / (1 + 2)

def test_selected_learned_hypothesis_is_sent_to_experiment():
experiment = HypothesisAwareExperiment(
result=15
)

engine = CognitiveExperimentEngine()

engine.experiment_loop.experiment = experiment

planner = engine.hypothesis_planner

planner.record_result(
    "use_recent_experience",
    10
)

planner.record_result(
    "increase_observation_frequency",
    2
)

result = engine.run_cycle(
    {
        "goal": "reduce_prediction_error"
    },
    10
)

assert result["status"] == "completed"

assert result["selected_hypothesis"]["hypothesis"] == (
    "increase_observation_frequency"
)

assert experiment.received_hypothesis["hypothesis"] == (
    "increase_observation_frequency"
)

assert experiment.received_hypothesis["learned"] is True

def test_hypothesis_learning_result_is_returned():
experiment = HypothesisAwareExperiment(
result=20
)

engine = CognitiveExperimentEngine()

engine.experiment_loop.experiment = experiment

result = engine.run_cycle(
    {
        "goal": "reduce_prediction_error"
    },
    10
)

assert result["status"] == "completed"

assert result["hypothesis_learning"]["status"] == "recorded"

assert result["hypothesis_learning"]["hypothesis"] == (
    "use_recent_experience"
)

assert result["hypothesis_learning"]["attempts"] == 1

assert result["hypothesis_learning"]["average_error"] == 10.0

def test_hypothesis_learning_improves_selection_across_cycles():
experiment = HypothesisAwareExperiment(
result=20
)

engine = CognitiveExperimentEngine()

engine.experiment_loop.experiment = experiment

first = engine.run_cycle(
    {
        "goal": "reduce_prediction_error"
    },
    10
)

assert first["status"] == "completed"

assert first["selected_hypothesis"]["hypothesis"] == (
    "use_recent_experience"
)

assert first["difference"] == 10

planner = engine.hypothesis_planner

planner.record_result(
    "increase_observation_frequency",
    2
)

reasoning = engine.reason(
    {
        "goal": "reduce_prediction_error"
    }
)

selected = reasoning["selected_hypothesis"]

assert selected["hypothesis"] == (
    "increase_observation_frequency"
)

assert selected["learned"] is True
assert selected["average_error"] == 2
assert selected["attempts"] == 1
assert selected["score"] == 1 / (1 + 2)

def test_learned_hypothesis_is_used_again_in_next_cycle():
experiment = HypothesisAwareExperiment(
result=10
)

engine = CognitiveExperimentEngine()

engine.experiment_loop.experiment = experiment

planner = engine.hypothesis_planner

planner.record_result(
    "use_recent_experience",
    10
)

planner.record_result(
    "increase_observation_frequency",
    2
)

first = engine.run_cycle(
    {
        "goal": "reduce_prediction_error"
    },
    10
)

assert first["status"] == "completed"

assert first["selected_hypothesis"]["hypothesis"] == (
    "increase_observation_frequency"
)

assert experiment.received_hypothesis["hypothesis"] == (
    "increase_observation_frequency"
)

learned = engine.get_learned_hypotheses()

selected_record = None

for record in learned:
    if record["hypothesis"] == (
        "increase_observation_frequency"
    ):
        selected_record = record
        break

assert selected_record is not None
assert selected_record["attempts"] == 2
assert selected_record["average_error"] == 1.0
