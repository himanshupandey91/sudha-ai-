"""
Sudha AI - Action Learning Loop

Connects:
    AdaptivePredictor
        ↓
    ActionEngine
        ↓
    Environment
        ↓
    Actual Result
        ↓
    AdaptivePredictor

The coordinator owns orchestration and action-to-hypothesis mapping.
"""

from __future__ import annotations


class ActionLearningLoop:
    def __init__(
        self,
        predictor,
        action_engine,
        environment,
        action_hypotheses,
        available_actions,
    ):
        if predictor is None:
            raise ValueError("predictor must not be None")

        if action_engine is None:
            raise ValueError("action_engine must not be None")

        if environment is None:
            raise ValueError("environment must not be None")

        if not isinstance(action_hypotheses, dict):
            raise TypeError("action_hypotheses must be a dictionary")

        if not isinstance(available_actions, list):
            raise TypeError("available_actions must be a list")

        self.predictor = predictor
        self.action_engine = action_engine
        self.environment = environment
        self.action_hypotheses = dict(action_hypotheses)
        self.available_actions = list(available_actions)

        self.history = []

    def run_cycle(self, goal_temperature):
        current_state = self.environment.get_state()

        predicted_effects = {}

        for action in self.available_actions:
            hypothesis = self.action_hypotheses.get(action)

            if hypothesis is None:
                continue

            prediction = self.predictor.predict(hypothesis)

            if isinstance(prediction, (int, float)):
                predicted_effects[action] = prediction

        selection = self.action_engine.select_action(
            {
                "current_state": current_state,
                "goal": {
                    "temperature": goal_temperature
                },
                "predicted_effects": predicted_effects,
                "available_actions": self.available_actions,
            }
        )

        if selection["status"] != "selected":
            return {
                "status": "rejected",
                "reason": selection["reason"],
            }

        selected_action = selection["action"]
        hypothesis = self.action_hypotheses.get(selected_action)

        if hypothesis is None:
            return {
                "status": "rejected",
                "reason": "selected_action_has_no_hypothesis",
            }

        before_temperature = current_state.get("temperature")

        result = self.environment.step(selected_action)

        actual_temperature = result["actual"]

        if not isinstance(before_temperature, (int, float)):
            return {
                "status": "rejected",
                "reason": "before_temperature_must_be_numeric",
            }

        if not isinstance(actual_temperature, (int, float)):
            return {
                "status": "rejected",
                "reason": "actual_temperature_must_be_numeric",
            }

        actual_effect = actual_temperature - before_temperature

        prediction_before_learning = self.predictor.predict(
            hypothesis
        )

        if not isinstance(
            prediction_before_learning,
            (int, float)
        ):
            return {
                "status": "rejected",
                "reason": "selected_action_prediction_missing",
            }

        prediction_error = abs(
            actual_effect - prediction_before_learning
        )

        learning = self.predictor.update(
            hypothesis=hypothesis,
            actual=actual_effect,
        )

        learned_prediction = self.predictor.predict(
            hypothesis
        )

        cycle_result = {
            "status": "completed",
            "action": selected_action,
            "hypothesis": hypothesis,
            "before_temperature": before_temperature,
            "predicted_effect": prediction_before_learning,
            "actual_effect": actual_effect,
            "prediction_error": prediction_error,
            "learned_prediction": learned_prediction,
            "actual_temperature": actual_temperature,
            "selection": selection,
            "environment_result": result,
            "learning": learning,
        }

        self.history.append(cycle_result)

        return cycle_result

    def run(self, goal_temperature, cycles=100):
        if not isinstance(cycles, int):
            raise TypeError("cycles must be an integer")

        if cycles <= 0:
            raise ValueError("cycles must be greater than 0")

        results = []

        for _ in range(cycles):
            result = self.run_cycle(
                goal_temperature=goal_temperature
            )

            if result["status"] != "completed":
                return {
                    "status": "rejected",
                    "reason": result["reason"],
                    "results": results,
                    "history": list(self.history),
                }

            results.append(result)

        errors = [
            result["prediction_error"]
            for result in results
        ]

        return {
            "status": "completed",
            "cycles": len(results),
            "results": results,
            "history": list(self.history),
            "initial_error": errors[0],
            "final_error": errors[-1],
            "error_reduction": errors[0] - errors[-1],
            "learned_predictions": {
                action: self.predictor.predict(hypothesis)
                for action, hypothesis
                in self.action_hypotheses.items()
            },
        }

    def get_history(self):
        return list(self.history)

    def clear_history(self):
        self.history.clear()

        return {
            "status": "cleared"
                          }
