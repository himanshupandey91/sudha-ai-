"""
Sudha AI - Adaptive Hypothesis Planning Engine

Version 0.3

Connects:

Goal
  ↓
Candidate Hypotheses
  ↓
Hypothesis Performance
  ↓
Exploration / Exploitation
  ↓
Adaptive Selection
  ↓
Plan

Version 0.3:
- Integrates HypothesisLearningEngine
- Uses learned performance when available
- Supports deterministic exploration of unseen hypotheses
- Keeps static priority as fallback when exploration is disabled
- Does not invent experiment results
- Deterministic behavior
- Bounded candidate generation
- No external side effects
"""

from core.hypothesis import HypothesisEngine
from core.planning import PlanningEngine
from core.hypothesis_learning import HypothesisLearningEngine


class HypothesisPlanningEngine:

    def __init__(
        self,
        hypothesis_engine=None,
        planning_engine=None,
        hypothesis_learning=None,
        exploration=False
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

        self.hypothesis_learning = (
            hypothesis_learning
            if hypothesis_learning is not None
            else HypothesisLearningEngine()
        )

        if not isinstance(exploration, bool):
            raise ValueError(
                "exploration must be a boolean"
            )

        self.exploration = exploration

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
        generated = self.generate_hypotheses(
            goal_state
        )

        if generated["status"] != "generated":
            return generated

        hypotheses = generated["hypotheses"]

        if not hypotheses:
            return {
                "status": "unavailable",
                "reason": "no_hypothesis_available"
            }

        learned = []
        unseen = []

        for candidate in hypotheses:
            name = candidate.get("hypothesis")

            if not isinstance(name, str):
                continue

            result = self.hypothesis_learning.evaluate(
                name
            )

            if result.get("status") == "unseen":
                unseen.append(candidate)
                continue

            learned.append(result)

        if self.exploration and unseen:
            selected = max(
                unseen,
                key=lambda item: item["priority"]
            )

            return {
                "status": "selected",
                "hypothesis": {
                    **dict(selected),
                    "learned": False,
                    "exploration": True
                }
            }

        if learned:
            learned.sort(
                key=lambda item: (
                    item["score"],
                    -item["average_error"]
                ),
                reverse=True
            )

            best = learned[0]

            return {
                "status": "selected",
                "hypothesis": {
                    "hypothesis": best["hypothesis"],
                    "priority": self._find_priority(
                        hypotheses,
                        best["hypothesis"]
                    ),
                    "learned": True,
                    "exploration": False,
                    "score": best["score"],
                    "average_error": best[
                        "average_error"
                    ],
                    "attempts": best["attempts"]
                }
            }

        best = max(
            hypotheses,
            key=lambda item: item["priority"]
        )

        return {
            "status": "selected",
            "hypothesis": {
                **dict(best),
                "learned": False,
                "exploration": False
            }
        }

    def record_result(
        self,
        hypothesis,
        difference
    ):
        try:
            return self.hypothesis_learning.record(
                hypothesis,
                difference
            )
        except Exception as error:
            return {
                "status": "failed",
                "reason": "hypothesis_result_recording_failed",
                "error": str(error)
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
            "hypotheses": hypotheses_result[
                "hypotheses"
            ],
            "selected_hypothesis": selected_result[
                "hypothesis"
            ],
            "plan": plan_result["plan"]
        }

    def get_learned_hypotheses(self):
        return self.hypothesis_learning.rank()

    def clear_learning(self):
        return self.hypothesis_learning.clear()

    def _find_priority(
        self,
        hypotheses,
        hypothesis_name
    ):
        for candidate in hypotheses:
            if candidate.get("hypothesis") == hypothesis_name:
                return candidate.get("priority")

        return 0

    def get_configuration(self):
        return {
            "hypothesis_engine": type(
                self.hypothesis
            ).__name__,
            "planning_engine": type(
                self.planning
            ).__name__,
            "hypothesis_learning": type(
                self.hypothesis_learning
            ).__name__,
            "exploration": self.exploration
        }
