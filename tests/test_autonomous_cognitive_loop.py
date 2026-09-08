"""
Autonomous cognitive execution loop.

The loop repeatedly gives observations to a cognitive engine, records each
completed cognitive cycle, and stops when either the configured cycle limit,
the observation sequence, or the cognitive engine stops execution.

This module does not invent observations or actual outcomes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence


class AutonomousCognitiveLoop:
    """
    Execute a CognitiveExperimentEngine across a bounded observation sequence.

    The cognitive engine must provide:
        - run_cycle(goal_state, observation)
        - is_stopped()

    Optional lifecycle methods:
        - stop()
        - reset()
    """

    def __init__(self, cognitive_engine: Any) -> None:
        if cognitive_engine is None:
            raise ValueError("cognitive_engine is required")

        run_cycle = getattr(cognitive_engine, "run_cycle", None)
        if not callable(run_cycle):
            raise TypeError(
                "cognitive_engine must provide a callable run_cycle"
            )

        self.cognitive_engine = cognitive_engine
        self._history: List[Dict[str, Any]] = []
        self._cycle_count = 0

    def _validate_goal(self, goal_state: Dict[str, Any]) -> None:
        """Validate the goal-state structure."""
        if not isinstance(goal_state, dict):
            raise TypeError("goal_state must be a dictionary")

        if "goal" not in goal_state:
            raise ValueError("goal_state must contain a goal")

        goal = goal_state["goal"]

        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("goal_state must contain a goal")

    def _validate_observations(
        self,
        observations: Sequence[Any],
    ) -> None:
        """Validate the legacy finite observation sequence."""
        if not isinstance(observations, (list, tuple)):
            raise TypeError("observations must be a list or tuple")

    def _validate_max_cycles(self, max_cycles: int) -> None:
        """Validate the maximum number of cycles."""
        if isinstance(max_cycles, bool) or not isinstance(max_cycles, int):
            raise TypeError("max_cycles must be an integer")

        if max_cycles <= 0:
            raise ValueError("max_cycles must be greater than zero")

    def run(
        self,
        goal_state: Dict[str, Any],
        observations: Optional[Sequence[Any]] = None,
        max_cycles: int = 1,
    ) -> Dict[str, Any]:
        """
        Run the autonomous cognitive loop.

        Parameters
        ----------
        goal_state:
            Dictionary containing a non-empty ``goal`` value.

        observations:
            Finite list or tuple of observations. The loop never creates
            observations itself.

        max_cycles:
            Maximum number of cognitive cycles to execute.

        Returns
        -------
        dict
            Structured execution result containing every completed cycle.

        Notes
        -----
        This method intentionally keeps the original finite-sequence API.
        Observation-provider support can be added separately without
        changing this baseline contract.
        """
        self._validate_goal(goal_state)

        if observations is None:
            raise TypeError("observations must be a list or tuple")

        self._validate_observations(observations)
        self._validate_max_cycles(max_cycles)

        self._history = []
        self._cycle_count = 0

        if len(observations) == 0:
            return {
                "status": "unavailable",
                "goal": goal_state,
                "cycles": [],
                "cycle_count": 0,
                "max_cycles": max_cycles,
                "reason": "no_observations",
                "stopped": False,
            }

        cycle_limit = min(max_cycles, len(observations))

        for index in range(cycle_limit):
            is_stopped = getattr(
                self.cognitive_engine,
                "is_stopped",
                None,
            )

            if callable(is_stopped) and is_stopped():
                return {
                    "status": "stopped",
                    "goal": goal_state,
                    "cycles": list(self._history),
                    "cycle_count": self._cycle_count,
                    "max_cycles": max_cycles,
                    "reason": "cognitive_engine_stopped",
                    "stopped": True,
                }

            observation = observations[index]

            cycle_result = self.cognitive_engine.run_cycle(
                goal_state,
                observation,
            )

            if not isinstance(cycle_result, dict):
                raise TypeError(
                    "cognitive_engine.run_cycle must return a dictionary"
                )

            if cycle_result.get("status") != "completed":
                raise RuntimeError(
                    "cognitive_engine.run_cycle must return "
                    "status='completed'"
                )

            self._history.append(cycle_result)
            self._cycle_count += 1

        if self._cycle_count >= max_cycles:
            reason = "max_cycles_reached"
        else:
            reason = "observations_exhausted"

        return {
            "status": "completed",
            "goal": goal_state,
            "cycles": list(self._history),
            "cycle_count": self._cycle_count,
            "max_cycles": max_cycles,
            "reason": reason,
            "stopped": False,
        }

    def stop(self) -> None:
        """Request the underlying cognitive engine to stop."""
        stop_method = getattr(self.cognitive_engine, "stop", None)

        if not callable(stop_method):
            raise AttributeError(
                "cognitive_engine must provide a callable stop method"
            )

        stop_method()

    def reset(self) -> None:
        """Reset the autonomous loop and the underlying cognitive engine."""
        reset_method = getattr(self.cognitive_engine, "reset", None)

        if not callable(reset_method):
            raise AttributeError(
                "cognitive_engine must provide a callable reset method"
            )

        reset_method()

        self._history = []
        self._cycle_count = 0

    def get_history(self) -> List[Dict[str, Any]]:
        """Return a copy of completed cognitive cycles."""
        return list(self._history)

    def get_cycle_count(self) -> int:
        """Return the number of completed cycles."""
        return self._cycle_count

    def is_stopped(self) -> bool:
        """Return whether the underlying cognitive engine is stopped."""
        is_stopped = getattr(
            self.cognitive_engine,
            "is_stopped",
            None,
        )

        if not callable(is_stopped):
            return False

        return bool(is_stopped())
