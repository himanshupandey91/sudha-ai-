"""
Sudha AI - Goal Generation Module

Version 0.1

Converts prediction error into a simple goal.
"""


class GoalEngine:

    def generate(self, state):
        """
        Generate a goal from the current system state.
        """

        if not state:
            return {
                "goal": "observe"
            }

        difference = state.get("difference", 0)

        if difference > 0:
            return {
                "goal": "reduce_prediction_error",
                "priority": difference
            }

        return {
            "goal": "continue_observation",
            "priority": 0
        }
