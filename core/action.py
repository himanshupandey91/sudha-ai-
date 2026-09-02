"""
Sudha AI - Action Module

Version 0.1

The Action Engine converts planned actions into
validated internal actions.

Important:
- No arbitrary shell commands.
- No unrestricted file operations.
- No network access.
- No external side effects.

This first version is intentionally controlled and deterministic.
"""


class ActionEngine:

    def __init__(self):
        """
        Define the actions that Sudha AI is currently
        allowed to execute.
        """

        self.allowed_actions = {
            "observe_new_data": self._observe_new_data,
            "make_new_prediction": self._make_new_prediction,
            "compare_prediction_with_actual": self._compare_prediction_with_actual,
        }

    def execute(self, action_name):
        """
        Validate and execute an internal action.

        Args:
            action_name: Name of the requested action.

        Returns:
            A structured result describing the action.
        """

        if action_name not in self.allowed_actions:
            return {
                "action": action_name,
                "status": "rejected",
                "reason": "action_not_allowed"
            }

        action_function = self.allowed_actions[action_name]

        return action_function()

    def execute_plan(self, plan):
        """
        Execute a complete validated plan.

        Args:
            plan: List of action names.

        Returns:
            List containing the result of every action.
        """

        if not isinstance(plan, list):
            return {
                "status": "rejected",
                "reason": "plan_must_be_a_list",
                "results": []
            }

        results = []

        for action_name in plan:
            result = self.execute(action_name)
            results.append(result)

            if result["status"] == "rejected":
                return {
                    "status": "rejected",
                    "reason": "plan_contains_invalid_action",
                    "results": results
                }

        return {
            "status": "completed",
            "results": results
        }

    def _observe_new_data(self):
        """Internal observation action."""

        return {
            "action": "observe_new_data",
            "status": "ready"
        }

    def _make_new_prediction(self):
        """Internal prediction action."""

        return {
            "action": "make_new_prediction",
            "status": "ready"
        }

    def _compare_prediction_with_actual(self):
        """Internal comparison action."""

        return {
            "action": "compare_prediction_with_actual",
            "status": "ready"
        }
