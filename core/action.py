"""
Sudha AI - Action Module

Version 0.2

The Action Engine converts planned actions into
validated internal operations.

Important:
- No arbitrary shell commands.
- No unrestricted file operations.
- No network access.
- No external side effects.
- Actions operate only on supplied internal context.

This version introduces real internal action processing.
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

    def execute(self, action_name, context=None):
        """
        Validate and execute an internal action.

        Args:
            action_name: Name of the requested action.
            context: Internal data required by the action.

        Returns:
            Structured result describing the action.
        """

        if action_name not in self.allowed_actions:
            return {
                "action": action_name,
                "status": "rejected",
                "reason": "action_not_allowed"
            }

        if context is None:
            context = {}

        if not isinstance(context, dict):
            return {
                "action": action_name,
                "status": "rejected",
                "reason": "context_must_be_a_dict"
            }

        action_function = self.allowed_actions[action_name]

        return action_function(context)

    def execute_plan(self, plan, context=None):
        """
        Execute a complete validated plan.

        Args:
            plan: List of action names.
            context: Shared internal context.

        Returns:
            Structured result containing every action result.
        """

        if not isinstance(plan, list):
            return {
                "status": "rejected",
                "reason": "plan_must_be_a_list",
                "results": []
            }

        if context is None:
            context = {}

        if not isinstance(context, dict):
            return {
                "status": "rejected",
                "reason": "context_must_be_a_dict",
                "results": []
            }

        results = []

        for action_name in plan:

            result = self.execute(
                action_name,
                context
            )

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

    def _observe_new_data(self, context):
        """
        Retrieve new observation from internal context.
        """

        if "observation" not in context:
            return {
                "action": "observe_new_data",
                "status": "rejected",
                "reason": "observation_not_available"
            }

        return {
            "action": "observe_new_data",
            "status": "completed",
            "observation": context["observation"]
        }

    def _make_new_prediction(self, context):
        """
        Retrieve the current prediction from internal context.
        """

        if "prediction" not in context:
            return {
                "action": "make_new_prediction",
                "status": "rejected",
                "reason": "prediction_not_available"
            }

        return {
            "action": "make_new_prediction",
            "status": "completed",
            "prediction": context["prediction"]
        }

    def _compare_prediction_with_actual(self, context):
        """
        Compare prediction with actual value.

        For numeric values, absolute error is calculated.
        For matching non-numeric values, error is 0.
        Otherwise error is 1.
        """

        if "prediction" not in context:
            return {
                "action": "compare_prediction_with_actual",
                "status": "rejected",
                "reason": "prediction_not_available"
            }

        if "actual" not in context:
            return {
                "action": "compare_prediction_with_actual",
                "status": "rejected",
                "reason": "actual_not_available"
            }

        prediction = context["prediction"]
        actual = context["actual"]

        if isinstance(prediction, (int, float)) and isinstance(actual, (int, float)):
            difference = abs(actual - prediction)

        elif prediction == actual:
            difference = 0

        else:
            difference = 1

        return {
            "action": "compare_prediction_with_actual",
            "status": "completed",
            "prediction": prediction,
            "actual": actual,
            "difference": difference
        }
