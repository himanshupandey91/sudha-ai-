"""
Deterministic Environment Layer for Sudha AI.

Version: 0.1.0

The environment is responsible for:
    Action -> State Transition -> Actual Observation

It does not perform prediction or learning.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


class EnvironmentError(Exception):
    """Base exception for environment errors."""


class Environment:
    """
    Small deterministic environment for causal-loop testing.

    State:
        A dictionary containing the current environment state.

    Supported actions:
        - increase_temperature
        - decrease_temperature
        - switch_on
        - switch_off
        - observe

    The environment changes its own state only through step().
    """

    SUPPORTED_ACTIONS = {
        "increase_temperature",
        "decrease_temperature",
        "switch_on",
        "switch_off",
        "observe",
    }

    def __init__(self, initial_state: Dict[str, Any] | None = None):
        if initial_state is None:
            initial_state = {
                "temperature": 20.0,
                "machine": "OFF",
            }

        if not isinstance(initial_state, dict):
            raise TypeError("initial_state must be a dictionary")

        self._initial_state = deepcopy(initial_state)
        self._state = deepcopy(initial_state)

    def reset(self) -> Dict[str, Any]:
        """
        Reset the environment to its original state.
        """
        self._state = deepcopy(self._initial_state)
        return self.get_state()

    def get_state(self) -> Dict[str, Any]:
        """
        Return a copy of the current environment state.
        """
        return deepcopy(self._state)

    def step(self, action: str) -> Dict[str, Any]:
        """
        Execute one action and return the resulting actual observation.

        The state transition happens here. No predicted value is used.
        """
        if not isinstance(action, str):
            raise TypeError("action must be a string")

        if action not in self.SUPPORTED_ACTIONS:
            raise ValueError(f"Unsupported action: {action}")

        before_state = self.get_state()

        if action == "increase_temperature":
            self._increase_temperature()

        elif action == "decrease_temperature":
            self._decrease_temperature()

        elif action == "switch_on":
            self._state["machine"] = "ON"

        elif action == "switch_off":
            self._state["machine"] = "OFF"

        elif action == "observe":
            pass

        after_state = self.get_state()

        return {
            "status": "completed",
            "action": action,
            "before_state": before_state,
            "after_state": after_state,
            "actual": self._actual_observation(),
        }

    def _increase_temperature(self) -> None:
        temperature = self._state.get("temperature")

        if not isinstance(temperature, (int, float)):
            raise EnvironmentError(
                "temperature must be numeric for increase_temperature"
            )

        self._state["temperature"] = temperature + 1.0

    def _decrease_temperature(self) -> None:
        temperature = self._state.get("temperature")

        if not isinstance(temperature, (int, float)):
            raise EnvironmentError(
                "temperature must be numeric for decrease_temperature"
            )

        self._state["temperature"] = temperature - 1.0

    def _actual_observation(self) -> Any:
        """
        Return the actual observable result after the transition.

        For this deterministic environment, temperature is the primary
        numeric observation used by the cognitive learning loop.
        """
        if "temperature" in self._state:
            return self._state["temperature"]

        return deepcopy(self._state)

    def get_configuration(self) -> Dict[str, Any]:
        """
        Return deterministic environment configuration.
        """
        return {
            "environment": self.__class__.__name__,
            "supported_actions": sorted(self.SUPPORTED_ACTIONS),
            "initial_state": deepcopy(self._initial_state),
            "current_state": self.get_state(),
        }
