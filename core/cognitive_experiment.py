"""
Sudha AI - Cognitive Experiment Engine

Version 0.1

Connects:

Goal
    ↓
Hypothesis
    ↓
Plan
    ↓
Experiment
    ↓
Actual Result
    ↓
Evaluation
    ↓
Learning
    ↓
Memory
    ↓
World Model

Design goals:
- Reuse existing Sudha AI components
- Explicit reasoning cycle
- No uncontrolled loops
- No external side effects
- Deterministic behavior
- Fully testable
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

        prediction = self.predict(observation)

        if prediction["status"] != "predicted":
            return prediction

        return {
            "status": "ready",
            "goal": goal_state.get("goal"),
            "hypotheses": reasoning["hypotheses"],
            "selected_hypothesis": reasoning[
                "selected_hypothesis"
            ],
            "plan": reasoning["plan"],
            "observation": observation,
            "prediction": prediction["prediction"]
        }

    def get_configuration(self):
        return {
            "hypothesis_planner": type(
                self.hypothesis_planner
            ).__name__,
            "experiment_loop": type(
                self.experiment_loop
            ).__name__
        }
