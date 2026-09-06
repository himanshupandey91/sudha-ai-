"""
Sudha AI - Cognitive Experiment Engine

Version 0.2

Connects:

Goal
    ↓
Hypothesis
    ↓
Plan
    ↓
Prediction
    ↓
Experiment
    ↓
Actual Result
    ↓
Difference
    ↓
Learning
    ↓
Memory
    ↓
World Model

Version 0.2:
- Preserves existing reasoning API.
- Connects reasoning to ExperimentLoopEngine.
- Executes a complete controlled experiment cycle.
- Returns prediction, actual result, difference and learning data.
- Uses existing closed-loop safety limits.
- No uncontrolled infinite loops.
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

    def run_cycle(self, goal_state, observation):
        reasoning = self.reason(goal_state)

        if reasoning["status"] != "ready":
            return reasoning

        experiment_result = self.experiment_loop.run_cycle(
            observation
        )

        if experiment_result["status"] not in (
            "completed",
            "stopped"
        ):
            return {
                "status": experiment_result["status"],
                "goal": goal_state.get("goal"),
                "hypotheses": reasoning["hypotheses"],
                "selected_hypothesis": reasoning[
                    "selected_hypothesis"
                ],
                "plan": reasoning["plan"],
                "observation": observation,
                "experiment": experiment_result
            }

        if experiment_result["status"] == "stopped":
            return {
                "status": "stopped",
                "goal": goal_state.get("goal"),
                "hypotheses": reasoning["hypotheses"],
                "selected_hypothesis": reasoning[
                    "selected_hypothesis"
                ],
                "plan": reasoning["plan"],
                "observation": observation,
                "experiment": experiment_result
            }

        return {
            "status": "completed",
            "goal": goal_state.get("goal"),
            "hypotheses": reasoning["hypotheses"],
            "selected_hypothesis": reasoning[
                "selected_hypothesis"
            ],
            "plan": reasoning["plan"],
            "observation": experiment_result["observation"],
            "prediction": experiment_result["prediction"],
            "actual": experiment_result["actual"],
            "difference": experiment_result["difference"],
            "learning": experiment_result["learning"],
            "world_model": experiment_result["world_model"],
            "cycle": experiment_result["cycle"],
            "stopped": experiment_result["stopped"]
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

    def get_configuration(self):
        return {
            "hypothesis_planner": type(
                self.hypothesis_planner
            ).__name__,
            "experiment_loop": type(
                self.experiment_loop
            ).__name__
        }
