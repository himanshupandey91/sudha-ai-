"""
Sudha AI - Action Module

Version 0.3

The Action Engine converts planned actions into
validated internal operations and can select an
action that is predicted to move the current state
toward a supplied goal.

Important:
- No arbitrary shell commands.
- No unrestricted file operations.
- No network access.
- No external side effects.
- Actions operate only on supplied internal context.

This version remains backward compatible with
the Version 0.1 and Version 0.2 action interface.
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

    def select_action(self, context):
        """
        Select the available action whose predicted effect
        moves the current state closest to the goal.

        Expected context:

        {
            "current_state": {
                "temperature": 20.0
            },
            "goal": {
                "temperature": 22.0
            },
            "predicted_effects": {
                "increase_temperature": 1.0,
                "decrease_temperature": -1.0
            },
            "available_actions": [
                "increase_temperature",
                "decrease_temperature"
            ]
        }

        The predicted effect is treated as a state delta.

        Example:

        current temperature = 20
        goal temperature = 22

        increase prediction = +1
        predicted next state = 21
        distance to goal = 1

        decrease prediction = -1
        predicted next state = 19
        distance to goal = 3

        Therefore:

        increase_temperature is selected.
        """

        if not isinstance(context, dict):
            return {
                "status": "rejected",
                "reason": "context_must_be_a_dict"
            }

        current_state = context.get("current_state")
        goal = context.get("goal")
        predicted_effects = context.get("predicted_effects")
        available_actions = context.get("available_actions")

        if not isinstance(current_state, dict):
            return {
                "status": "rejected",
                "reason": "current_state_must_be_a_dict"
            }

        if not isinstance(goal, dict):
            return {
                "status": "rejected",
                "reason": "goal_must_be_a_dict"
            }

        if not isinstance(predicted_effects, dict):
            return {
                "status": "rejected",
                "reason": "predicted_effects_must_be_a_dict"
            }

        if not isinstance(available_actions, list):
            return {
                "status": "rejected",
                "reason": "available_actions_must_be_a_list"
            }

        if not available_actions:
            return {
                "status": "rejected",
                "reason": "no_available_actions"
            }

        if "temperature" not in current_state:
            return {
                "status": "rejected",
                "reason": "current_temperature_missing"
            }

        if "temperature" not in goal:
            return {
                "status": "rejected",
                "reason": "goal_temperature_missing"
            }

        current_temperature = current_state["temperature"]
        goal_temperature = goal["temperature"]

        if not isinstance(current_temperature, (int, float)):
            return {
                "status": "rejected",
                "reason": "current_temperature_must_be_numeric"
            }

        if not isinstance(goal_temperature, (int, float)):
            return {
                "status": "rejected",
                "reason": "goal_temperature_must_be_numeric"
            }

        candidates = []

        for action_name in available_actions:

            if action_name not in predicted_effects:
                continue

            predicted_effect = predicted_effects[action_name]

            if not isinstance(predicted_effect, (int, float)):
                continue

            predicted_temperature = (
                current_temperature + predicted_effect
            )

            distance_to_goal = abs(
                goal_temperature - predicted_temperature
            )

            candidates.append({
                "action": action_name,
                "predicted_effect": predicted_effect,
                "predicted_temperature": predicted_temperature,
                "distance_to_goal": distance_to_goal
            })

        if not candidates:
            return {
                "status": "rejected",
                "reason": "no_valid_action_predictions"
            }

        selected = min(
            candidates,
            key=lambda candidate: candidate["distance_to_goal"]
        )

        return {
            "status": "selected",
            "action": selected["action"],
            "predicted_effect": selected["predicted_effect"],
            "predicted_state": {
                "temperature": selected["predicted_temperature"]
            },
            "distance_to_goal": selected["distance_to_goal"],
            "candidates": candidates
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
