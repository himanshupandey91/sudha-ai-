"""
Sudha AI - Experiment Loop Integration

Version 0.1

Connects:

Hypothesis / Prediction
        ↓
Experiment
        ↓
Observed Result
        ↓
Difference
        ↓
Learning
        ↓
Memory
        ↓
World Model

Design goals:
- Controlled experiment execution
- Explicit observed outcomes
- Closed-loop learning
- No uncontrolled infinite loops
- No external side effects
- Deterministic and testable
"""

from core.closed_loop import ClosedLoopLearningEngine


class ExperimentLoopEngine:

    def __init__(
        self,
        closed_loop=None,
        experiment=None,
        max_cycles=10
    ):
        self.closed_loop = (
            closed_loop
            if closed_loop is not None
            else ClosedLoopLearningEngine(
                max_cycles=max_cycles
            )
        )

        self.experiment = experiment

    def predict(self, observation):
        return self.closed_loop.predict(observation)

    def run_experiment(self, observation):
        if self.closed_loop.is_stopped():
            return {
                "status": "stopped",
                "reason": "closed_loop_stopped"
            }

        if self.experiment is None:
            return {
                "status": "unavailable",
                "reason": "experiment_not_configured"
            }

        execute = getattr(self.experiment, "run", None)

        if not callable(execute):
            return {
                "status": "rejected",
                "reason": "invalid_experiment"
            }

        try:
            actual = execute(observation)
        except Exception as error:
            return {
                "status": "failed",
                "reason": "experiment_execution_failed",
                "error": str(error)
            }

        return {
            "status": "experiment_completed",
            "observation": observation,
            "actual": actual
        }

    def run_cycle(self, observation):
        prediction_result = self.predict(observation)

        if prediction_result["status"] != "predicted":
            return prediction_result

        experiment_result = self.run_experiment(observation)

        if experiment_result["status"] != "experiment_completed":
            return experiment_result

        actual = experiment_result["actual"]

        learning_result = self.closed_loop.learn(
            observation=observation,
            prediction=prediction_result["prediction"],
            actual=actual
        )

        return {
            "status": "completed",
            "observation": observation,
            "prediction": prediction_result["prediction"],
            "actual": actual,
            "difference": learning_result["cycle"]["difference"],
            "learning": learning_result["cycle"]["learning"],
            "world_model": learning_result["cycle"]["world_model"],
            "cycle": learning_result["cycle"],
            "stopped": learning_result["stopped"]
        }

    def stop(self):
        return self.closed_loop.stop()

    def reset(self):
        return self.closed_loop.reset()

    def get_history(self):
        return self.closed_loop.get_history()

    def get_cycle_count(self):
        return self.closed_loop.get_cycle_count()

    def is_stopped(self):
        return self.closed_loop.is_stopped()
