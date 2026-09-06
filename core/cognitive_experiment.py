"""
Sudha AI - Cognitive Experiment Engine

Version 0.3

Connects:
Goal
    ↓
Hypothesis Generation
    ↓
Hypothesis Selection
    ↓
Plan
    ↓
Selected Hypothesis
    ↓
Experiment
    ↓
Actual Result
    ↓
Prediction Error
    ↓
Hypothesis Learning
    ↓
Memory
    ↓
World Model

Version 0.3:
- Passes the selected hypothesis to experiments that explicitly support it.
- Preserves compatibility with legacy experiments that only accept observation.
- Records the selected hypothesis after the experiment result is known.
- Does not invent experiment results.
- Keeps hypothesis attribution explicit.
- No uncontrolled loops.
- No external side effects by itself.
- Fully testable.
"""

from core.hypothesis_planner import HypothesisPlanningEngine
from core.experiment_loop import ExperimentLoopEngine


class CognitiveExperimentEngine:

    def __init__(
        self,
        hypothesis_planner=None,
        experiment_loop=None
    ):
        self.hypothesis_planner = (
            hypothesis_planner
            if hypothesis_planner is not None
            else HypothesisPlanningEngine()
        )

        self.experiment_loop = (
            experiment_loop
            if experiment_loop is not None
            else ExperimentLoopEngine()
        )

    def reason(self, goal_state):
        return self.hypothesis_planner.create_reasoning_plan(
            goal_state
        )

    def predict(self, observation):
        return self.experiment_loop.predict(
            observation
        )

    def run_experiment(
        self,
        observation,
        hypothesis=None
    ):
        if self.experiment_loop.is_stopped():
            return {
                "status": "stopped",
                "reason": "closed_loop_stopped"
            }

        experiment = self.experiment_loop.experiment

        if experiment is None:
            return {
                "status": "unavailable",
                "reason": "experiment_not_configured"
            }

        execute = getattr(
            experiment,
            "run",
            None
        )

        if not callable(execute):
            return {
                "status": "rejected",
                "reason": "invalid_experiment"
            }

        try:
            if hypothesis is not None:
                actual = execute(
                    observation,
                    hypothesis=hypothesis
                )
            else:
                actual = execute(observation)

        except TypeError:
            if hypothesis is None:
                return {
                    "status": "failed",
                    "reason": "experiment_execution_failed",
                    "error": (
                        "experiment_does_not_support_required_interface"
                    )
                }

            try:
                actual = execute(observation)

            except Exception as error:
                return {
                    "status": "failed",
                    "reason": "experiment_execution_failed",
                    "error": str(error)
                }

        except Exception as error:
            return {
                "status": "failed",
                "reason": "experiment_execution_failed",
                "error": str(error)
            }

        return {
            "status": "experiment_completed",
            "observation": observation,
            "hypothesis": hypothesis,
            "actual": actual
        }

    def run_cycle(
        self,
        goal_state,
        observation
    ):
        reasoning = self.reason(
            goal_state
        )

        if reasoning["status"] != "ready":
            return reasoning

        selected_hypothesis = reasoning[
            "selected_hypothesis"
        ]

        hypothesis_name = selected_hypothesis.get(
            "hypothesis"
        )

        prediction = self.predict(
            observation
        )

        if prediction["status"] != "predicted":
            return prediction

        experiment_result = self.run_experiment(
            observation=observation,
            hypothesis=selected_hypothesis
        )

        if experiment_result["status"] != "experiment_completed":
            return experiment_result

        actual = experiment_result["actual"]

        learning_result = (
            self.experiment_loop.closed_loop.learn(
                observation=observation,
                prediction=prediction["prediction"],
                actual=actual
            )
        )

        difference = learning_result[
            "cycle"
        ]["difference"]

        hypothesis_learning = (
            self.hypothesis_planner.record_result(
                hypothesis=hypothesis_name,
                difference=difference
            )
        )

        return {
            "status": "completed",
            "goal": goal_state.get("goal"),
            "hypotheses": reasoning["hypotheses"],
            "selected_hypothesis": selected_hypothesis,
            "plan": reasoning["plan"],
            "observation": observation,
            "prediction": prediction["prediction"],
            "actual": actual,
            "difference": difference,
            "learning": learning_result[
                "cycle"
            ]["learning"],
            "world_model": learning_result[
                "cycle"
            ]["world_model"],
            "hypothesis_learning": hypothesis_learning,
            "cycle": learning_result["cycle"],
            "stopped": learning_result["stopped"]
        }

    def stop(self):
        return self.experiment_loop.stop()

    def reset(self):
        return self.experiment_loop.reset()

    def get_history(self):
        return self.experiment_loop.get_history()

    def get_cycle_count(self):
        return self.experiment_loop.get_cycle_count()

    def is_stopped(self):
        return self.experiment_loop.is_stopped()

    def get_learned_hypotheses(self):
        return self.hypothesis_planner.get_learned_hypotheses()

    def clear_learning(self):
        return self.hypothesis_planner.clear_learning()

    def get_configuration(self):
        return {
            "hypothesis_planner": type(
                self.hypothesis_planner
            ).__name__,
            "experiment_loop": type(
                self.experiment_loop
            ).__name__
        }
