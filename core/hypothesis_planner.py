"""
Sudha AI - Hypothesis Planning Engine

Version 0.1

Connects:

Goal
  ↓
Hypothesis Generation
  ↓
Hypothesis Selection
  ↓
Plan Generation

Design goals:
- Reuse existing HypothesisEngine
- Reuse existing PlanningEngine
- Deterministic behavior
- Explicit hypothesis selection
- Explicit planning
- Bounded candidate generation
- No external side effects
- Fully testable
"""

from core.hypothesis import HypothesisEngine
from core.planning import PlanningEngine


class HypothesisPlanningEngine:

    def __init__(
        self,
        hypothesis_engine=None,
        planning_engine=None
    ):
        self.hypothesis = (
            hypothesis_engine
            if hypothesis_engine is not None
            else HypothesisEngine()
        )

        self.planning = (
            planning_engine
            if planning_engine is not None
            else PlanningEngine()
        )

    def generate_hypotheses(self, goal_state):
        try:
            hypotheses = self.hypothesis.generate(
                goal_state
            )
        except Exception as error:
            return {
                "status": "failed",
                "reason": "hypothesis_generation_failed",
                "error": str(error)
            }

        return {
            "status": "generated",
            "hypotheses": hypotheses,
            "count": len(hypotheses)
        }

    def select_hypothesis(self, goal_state):
        try:
            hypothesis = self.hypothesis.best(
                goal_state
            )
        except Exception as error:
            return {
                "status": "failed",
                "reason": "hypothesis_selection_failed",
                "error": str(error)
            }

        if hypothesis is None:
            return {
                "status": "unavailable",
                "reason": "no_hypothesis_available"
            }

        return {
            "status": "selected",
            "hypothesis": hypothesis
        }

    def create_plan(self, goal_state):
        try:
            plan = self.planning.create_plan(
                goal_state
            )
        except Exception as error:
            return {
                "status": "failed",
                "reason": "planning_failed",
                "error": str(error)
            }

        return {
            "status": "planned",
            "plan": plan
        }

    def create_reasoning_plan(self, goal_state):
        hypotheses_result = self.generate_hypotheses(
            goal_state
        )

        if hypotheses_result["status"] != "generated":
            return hypotheses_result

        selected_result = self.select_hypothesis(
            goal_state
        )

        if selected_result["status"] != "selected":
            return selected_result

        plan_result = self.create_plan(
            goal_state
        )

        if plan_result["status"] != "planned":
            return plan_result

        return {
            "status": "ready",
            "goal": goal_state.get("goal"),
            "hypotheses": hypotheses_result["hypotheses"],
            "selected_hypothesis": selected_result["hypothesis"],
            "plan": plan_result["plan"]
        }

    def get_configuration(self):
        return {
            "hypothesis_engine": type(
                self.hypothesis
            ).__name__,
            "planning_engine": type(
                self.planning
            ).__name__
        }
