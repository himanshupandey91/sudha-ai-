"""
Sudha AI - Cognitive Experiment Engine

Version 0.4.1

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
Learning
 ↓
World Model Update
"""

from core.hypothesis_planner import hypothesis_planner
from core.experiment import ExperimentEngine
from core.world_model import WorldModel


class CognitiveExperimentEngine:

    def __init__(
        self,
        hypothesis_planner_engine=None,
        experiment_engine=None,
        world_model=None
    ):
        self.hypothesis_planner = (
            hypothesis_planner_engine
            if hypothesis_planner_engine is not None
            else hypothesis_planner
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
        goal_state = goal_state or {}

        selector = getattr(
            self.hypothesis_planner,
            "select",
            None
        )

        if not callable(selector):
            return {
                "status": "unavailable",
                "reason": "hypothesis_selector_not_available"
            }

        hypothesis = selector(goal_state)

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
        goal_state = goal_state or {}
        observation = observation or {}

        reasoning = self.reason(goal_state)

        if reasoning["status"] != "ready":
            return reasoning

        hypothesis = reasoning["hypothesis"]

        predictor = getattr(
            self.hypothesis_planner,
            "predict",
            None
        )

        if callable(predictor):
            prediction = predictor(
                hypothesis,
                observation
            )
        else:
            prediction = {
                "hypothesis": hypothesis,
                "observation": observation
            }

        if actual is None:
            return {
                "status": "ready",
                "reason": "awaiting_actual_outcome",
                "hypothesis": hypothesis,
                "prediction": prediction
            }

        runner = getattr(
            self.experiment_engine,
            "run",
            None
        )

        if not callable(runner):
            return {
                "status": "failed",
                "reason": "experiment_runner_not_available"
            }

        try:
            experiment_result = runner(
                hypothesis=hypothesis,
                prediction=prediction,
                actual=actual
            )
        except TypeError:
            experiment_result = runner(
                actual=actual
            )

        if not isinstance(experiment_result, dict):
            return {
                "status": "failed",
                "reason": "invalid_experiment_result"
            }

        difference = experiment_result.get("difference")

        if difference is None:
            return {
                "status": "failed",
                "reason": "experiment_difference_missing"
            }

        recorder = getattr(
            self.hypothesis_planner,
            "record_result",
            None
        )

        if callable(recorder):
            recorder(
                hypothesis,
                difference
            )

        updater = getattr(
            self.world_model,
            "update",
            None
        )

        if callable(updater):
            updater(
                prediction=prediction,
                actual=actual,
                difference=difference
            )

        state_getter = getattr(
            self.world_model,
            "get_state",
            None
        )

        world_state = (
            state_getter()
            if callable(state_getter)
            else {}
        )

        result = {
            "status": "completed",
            "hypothesis": hypothesis,
            "prediction": prediction,
            "actual": actual,
            "difference": difference,
            "experiment": experiment_result,
            "world_model": world_state
        }

        self.history.append(result)

        return result

    def get_history(self):
        return list(self.history)

    def clear_history(self):
        self.history.clear()
