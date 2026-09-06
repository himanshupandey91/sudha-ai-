"""
Sudha AI - Cognitive Experiment Engine

Version 0.4

Real adaptive cognitive cycle:

Goal
 ↓
Hypothesis Selection
 ↓
Prediction
 ↓
Experiment
 ↓
Actual Outcome
 ↓
Difference
 ↓
Evaluation
 ↓
Learning
 ↓
World Model Update

No fake actual outcome is generated here.
"""

from core.hypothesis_planner import HypothesisPlanner
from core.experiment import ExperimentEngine
from core.world_model import WorldModel


class CognitiveExperimentEngine:

    def __init__(
        self,
        hypothesis_planner=None,
        experiment_engine=None,
        world_model=None
    ):
        self.hypothesis_planner = (
            hypothesis_planner
            if hypothesis_planner is not None
            else HypothesisPlanner()
        )

        self.experiment_engine = (
            experiment_engine
            if experiment_engine is not None
            else ExperimentEngine()
        )

        self.world_model = (
            world_model
            if world_model is not None
            else WorldModel()
        )

        self.history = []

    def reason(self, goal_state=None):
        """
        Select a hypothesis for the supplied goal.
        """

        goal_state = goal_state or {}

        hypothesis = self.hypothesis_planner.select(
            goal_state
        )

        if hypothesis is None:
            return {
                "status": "unavailable",
                "reason": "no_hypothesis_available"
            }

        return {
            "status": "ready",
            "hypothesis": hypothesis
        }

    def run_cycle(
        self,
        goal_state=None,
        observation=None,
        actual=None
    ):
        """
        Execute one complete cognitive experiment cycle.

        `actual` must be supplied by the experiment/environment.
        This engine never invents an actual outcome.
        """

        goal_state = goal_state or {}
        observation = observation or {}

        reasoning = self.reason(goal_state)

        if reasoning["status"] != "ready":
            return reasoning

        hypothesis = reasoning["hypothesis"]

        prediction = self.hypothesis_planner.predict(
            hypothesis,
            observation
        )

        if actual is None:
            return {
                "status": "ready",
                "reason": "awaiting_actual_outcome",
                "hypothesis": hypothesis,
                "prediction": prediction
            }

        experiment_result = self.experiment_engine.run(
            hypothesis=hypothesis,
            prediction=prediction,
            actual=actual
        )

        if not isinstance(experiment_result, dict):
            return {
                "status": "failed",
                "reason": "invalid_experiment_result"
            }

        difference = experiment_result.get(
            "difference"
        )

        if difference is None:
            return {
                "status": "failed",
                "reason": "experiment_difference_missing"
            }

        self.hypothesis_planner.record_result(
            hypothesis,
            difference
        )

        self.world_model.update(
            prediction=prediction,
            actual=actual,
            difference=difference
        )

        result = {
            "status": "completed",
            "hypothesis": hypothesis,
            "prediction": prediction,
            "actual": actual,
            "difference": difference,
            "experiment": experiment_result,
            "world_model": self.world_model.get_state()
        }

        self.history.append(result)

        return result

    def get_history(self):
        return list(self.history)

    def clear_history(self):
        self.history.clear()
