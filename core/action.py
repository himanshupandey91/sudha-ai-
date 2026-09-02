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

This version remains backward compatible with
the Version 0.1 action interface.
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

        If no context is supplied, the action remains
        compatible with Version 0.1 and returns "ready".

        If context is supplied, the action can process
        real internal data.
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

        If no context is supplied, actions retain their
        Version 0.1 "ready" behavior.

        With context, actions process supplied internal data.
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
        Observation action.

        Without observation data:
        preserve Version 0.1 behavior.

        With observation data:
        return the supplied observation.
        """

        if "observation" not in context:
            return {
                "action": "observe_new_data",
                "status": "ready"
            }

        return {
            "action": "observe_new_data",
            "status": "completed",
            "observation": context["observation"]
        }

    def _make_new_prediction(self, context):
        """
        Prediction action.

        Without prediction data:
        preserve Version 0.1 behavior.

        With prediction data:
        return the supplied prediction.
        """

        if "prediction" not in context:
            return {
                "action": "make_new_prediction",
                "status": "ready"
            }

        return {
            "action": "make_new_prediction",
            "status": "completed",
            "prediction": context["prediction"]
        }

    def _compare_prediction_with_actual(self, context):
        """
        Compare prediction with actual value.

        Without prediction or actual data:
        preserve Version 0.1 behavior.

        With both values:
        calculate prediction error.
        """

        if "prediction" not in context or "actual" not in context:
            return {
                "action": "compare_prediction_with_actual",
                "status": "ready"
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
