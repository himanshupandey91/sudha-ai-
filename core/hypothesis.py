"""
Sudha AI - Hypothesis Engine

Version 0.1

Generates and ranks candidate hypotheses for a goal.

Design goals:
- Deterministic behavior
- Multiple candidate hypotheses
- Explicit ranking
- Bounded hypothesis generation
- Fully testable
- No external side effects
"""


class HypothesisEngine:

    def __init__(self, max_hypotheses=5):
        """
        Initialize the Hypothesis Engine.

        max_hypotheses:
            Maximum number of hypotheses generated
            for a single goal.
        """

        if not isinstance(max_hypotheses, int):
            raise TypeError(
                "max_hypotheses must be an integer"
            )

        if max_hypotheses <= 0:
            raise ValueError(
                "max_hypotheses must be greater than zero"
            )

        self.max_hypotheses = max_hypotheses

    def generate(self, goal_state):
        """
        Generate candidate hypotheses from a goal.

        Returns:
            A list of structured hypotheses.
        """

        if not isinstance(goal_state, dict):
            raise TypeError(
                "goal_state must be a dictionary"
            )

        goal = goal_state.get("goal")

        if goal is None:
            return []

        candidates = []

        if goal == "reduce_prediction_error":
            candidates = [
                {
                    "hypothesis": "use_recent_experience",
                    "priority": 3
                },
                {
                    "hypothesis": "increase_observation_frequency",
                    "priority": 2
                },
                {
                    "hypothesis": "change_prediction_strategy",
                    "priority": 1
                }
            ]

        elif goal == "continue_observation":
            candidates = [
                {
                    "hypothesis": "collect_more_observations",
                    "priority": 1
                }
            ]

        else:
            candidates = [
                {
                    "hypothesis": "collect_more_information",
                    "priority": 1
                }
            ]

        candidates.sort(
            key=lambda item: item["priority"],
            reverse=True
        )

        return candidates[:self.max_hypotheses]

    def best(self, goal_state):
        """
        Return the highest-priority hypothesis.

        Returns:
            Best hypothesis or None.
        """

        hypotheses = self.generate(
            goal_state
        )

        if not hypotheses:
            return None

        return hypotheses[0]
