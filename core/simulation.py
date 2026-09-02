"""
Sudha AI - Simulation Engine

Version 0.1

Simulates candidate hypotheses before execution.

Design goals:
- Deterministic behavior
- Explicit simulation rules
- No external side effects
- No arbitrary code execution
- Fully testable
"""


class SimulationEngine:

    def __init__(self):
        """
        Initialize the Simulation Engine.

        Simulation rules are explicitly defined.
        """

        self.allowed_hypotheses = {
            "use_recent_experience":
                self._simulate_recent_experience,

            "increase_observation_frequency":
                self._simulate_more_observation,

            "change_prediction_strategy":
                self._simulate_prediction_strategy,

            "collect_more_observations":
                self._simulate_collect_observations,

            "collect_more_information":
                self._simulate_collect_information,
        }

    def simulate(self, hypothesis, state=None):
        """
        Simulate a hypothesis against the current state.

        Args:
            hypothesis:
                Name of the hypothesis to simulate.

            state:
                Current internal state.

        Returns:
            Structured simulation result.
        """

        if not isinstance(hypothesis, str):
            return {
                "status": "rejected",
                "reason": "hypothesis_must_be_a_string"
            }

        if hypothesis not in self.allowed_hypotheses:
            return {
                "status": "rejected",
                "reason": "hypothesis_not_allowed",
                "hypothesis": hypothesis
            }

        if state is None:
            state = {}

        if not isinstance(state, dict):
            return {
                "status": "rejected",
                "reason": "state_must_be_a_dictionary"
            }

        simulation_function = self.allowed_hypotheses[
            hypothesis
        ]

        return simulation_function(state)

    def _simulate_recent_experience(self, state):
        """
        Simulate using previous experience.

        Expected effect:
        reduce prediction error.
        """

        difference = state.get("difference", 0)

        if isinstance(difference, (int, float)):
            predicted_difference = difference * 0.5
        else:
            predicted_difference = None

        return {
            "status": "completed",
            "hypothesis": "use_recent_experience",
            "predicted_effect": "reduce_prediction_error",
            "current_difference": difference,
            "predicted_difference": predicted_difference
        }

    def _simulate_more_observation(self, state):
        """
        Simulate increased observation frequency.
        """

        difference = state.get("difference", 0)

        if isinstance(difference, (int, float)):
            predicted_difference = difference * 0.8
        else:
            predicted_difference = None

        return {
            "status": "completed",
            "hypothesis": "increase_observation_frequency",
            "predicted_effect": "improve_information",
            "current_difference": difference,
            "predicted_difference": predicted_difference
        }

    def _simulate_prediction_strategy(self, state):
        """
        Simulate changing the prediction strategy.
        """

        difference = state.get("difference", 0)

        if isinstance(difference, (int, float)):
            predicted_difference = difference * 0.7
        else:
            predicted_difference = None

        return {
            "status": "completed",
            "hypothesis": "change_prediction_strategy",
            "predicted_effect": "reduce_prediction_error",
            "current_difference": difference,
            "predicted_difference": predicted_difference
        }

    def _simulate_collect_observations(self, state):
        """
        Simulate collecting additional observations.
        """

        return {
            "status": "completed",
            "hypothesis": "collect_more_observations",
            "predicted_effect": "increase_information",
            "predicted_information_gain": 1
        }

    def _simulate_collect_information(self, state):
        """
        Simulate collecting additional information.
        """

        return {
            "status": "completed",
            "hypothesis": "collect_more_information",
            "predicted_effect": "increase_information",
            "predicted_information_gain": 1
        }
