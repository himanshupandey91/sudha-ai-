"""
Sudha AI - Planning Module

Version 0.1

Converts a goal into a simple sequence of planned steps.
"""


class PlanningEngine:

    def create_plan(self, goal_state):
        """
        Create a plan from the current goal.
        """

        if not goal_state:
            return {
                "goal": None,
                "plan": []
            }

        goal = goal_state.get("goal")

        if goal == "reduce_prediction_error":
            return {
                "goal": goal,
                "plan": [
                    "observe_new_data",
                    "make_new_prediction",
                    "compare_prediction_with_actual"
                ]
            }

        if goal == "continue_observation":
            return {
                "goal": goal,
                "plan": [
                    "observe_new_data"
                ]
            }

        return {
            "goal": goal,
            "plan": [
                "observe_new_data"
            ]
        }
