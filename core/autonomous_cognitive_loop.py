"""
Sudha AI - Autonomous Cognitive Loop

Version: 0.2

Connects a cognitive engine to an observation provider.

The loop supports two modes:

1. Backward-compatible supplied observations:
       run(goal_state, observations=[...], max_cycles=...)

2. Autonomous observation acquisition:
       run(
           goal_state,
           observation_provider=provider,
           max_cycles=...
       )

The autonomous mode obtains exactly one new observation from the
provider on every cycle.

The loop never invents observations or actual outcomes.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional


class AutonomousCognitiveLoop:
    """
    Repeatedly executes cognitive cycles.

    A cognitive engine must provide:

        run_cycle(goal_state, observation)

    It must also provide:

        is_stopped()

    The observation provider must provide:

        observe()

    and may optionally provide:

        reset()
    """

    def __init__(self, cognitive_engine):
        if cognitive_engine is None:
            raise ValueError("cognitive_engine is required")

        run_cycle = getattr(cognitive_engine, "run_cycle", None)
        if not callable(run_cycle):
            raise TypeError("cognitive_engine must provide run_cycle")

        is_stopped = getattr(cognitive_engine, "is_stopped", None)
        if not callable(is_stopped):
            raise TypeError("cognitive_engine must provide is_stopped")

        self.cognitive_engine = cognitive_engine

        self._history: list[dict] = []
        self._cycle_count = 0
        self._stopped = False

    def run(
        self,
        goal_state: dict,
        observations: Optional[Iterable[Any]] = None,
        max_cycles: int = 1,
        observation_provider=None,
    ) -> dict:
        """
        Execute autonomous cognitive cycles.

        Exactly one observation source must be supplied:

            observations
        or
            observation_provider

        ``observations`` is retained for backward compatibility.

        When an observation provider is supplied, one observation is
        acquired from the provider before every cognitive cycle.
        """

        self._validate_goal(goal_state)
        self._validate_max_cycles(max_cycles)

        if observations is not None and observation_provider is not None:
            raise ValueError(
                "provide either observations or observation_provider, not both"
            )

        if observation_provider is not None:
            return self._run_with_provider(
                goal_state=goal_state,
                observation_provider=observation_provider,
                max_cycles=max_cycles,
            )

        if observations is None:
            raise ValueError(
                "either observations or observation_provider is required"
            )

        observation_list = self._validate_observations(observations)

        if len(observation_list) == 0:
            return {
                "status": "unavailable",
                "goal": goal_state,
                "cycles": 0,
                "cycle_count": self._cycle_count,
                "max_cycles": max_cycles,
                "reason": "no_observations",
                "stopped": self._is_stopped(),
            }

        cycle_limit = min(max_cycles, len(observation_list))

        return self._execute_cycles(
            goal_state=goal_state,
            observations=observation_list[:cycle_limit],
            max_cycles=max_cycles,
            exhaustion_reason="observations_exhausted",
        )

    def _run_with_provider(
        self,
        goal_state: dict,
        observation_provider,
        max_cycles: int,
    ) -> dict:
        """
        Execute cycles using a live observation provider.
        """

        self._validate_observation_provider(observation_provider)

        if self._is_stopped():
            return {
                "status": "stopped",
                "goal": goal_state,
                "cycles": 0,
                "cycle_count": self._cycle_count,
                "max_cycles": max_cycles,
                "reason": "stopped_before_cycle",
                "stopped": True,
            }

        cycles = 0

        while cycles < max_cycles:
            if self._is_stopped():
                return {
                    "status": "stopped",
                    "goal": goal_state,
                    "cycles": cycles,
                    "cycle_count": self._cycle_count,
                    "max_cycles": max_cycles,
                    "reason": "stopped",
                    "stopped": True,
                }

            try:
                observation = observation_provider.observe()
            except StopIteration:
                if cycles == 0:
                    return {
                        "status": "unavailable",
                        "goal": goal_state,
                        "cycles": 0,
                        "cycle_count": self._cycle_count,
                        "max_cycles": max_cycles,
                        "reason": "observation_provider_exhausted",
                        "stopped": self._is_stopped(),
                    }

                return {
                    "status": "completed",
                    "goal": goal_state,
                    "cycles": cycles,
                    "cycle_count": self._cycle_count,
                    "max_cycles": max_cycles,
                    "reason": "observation_provider_exhausted",
                    "stopped": self._is_stopped(),
                }

            result = self._run_single_cycle(
                goal_state=goal_state,
                observation=observation,
            )

            cycles += 1

            if result.get("status") != "completed":
                return {
                    "status": result.get("status", "failed"),
                    "goal": goal_state,
                    "cycles": cycles,
                    "cycle_count": self._cycle_count,
                    "max_cycles": max_cycles,
                    "reason": result.get("reason", "cycle_failed"),
                    "stopped": self._is_stopped(),
                    "last_cycle": result,
                }

        return {
            "status": "completed",
            "goal": goal_state,
            "cycles": cycles,
            "cycle_count": self._cycle_count,
            "max_cycles": max_cycles,
            "reason": "max_cycles_reached",
            "stopped": self._is_stopped(),
        }

    def _execute_cycles(
        self,
        goal_state: dict,
        observations: list[Any],
        max_cycles: int,
        exhaustion_reason: str,
    ) -> dict:
        """
        Execute a finite supplied observation sequence.
        """

        cycles = 0

        for observation in observations:
            if self._is_stopped():
                return {
                    "status": "stopped",
                    "goal": goal_state,
                    "cycles": cycles,
                    "cycle_count": self._cycle_count,
                    "max_cycles": max_cycles,
                    "reason": "stopped",
                    "stopped": True,
                }

            result = self._run_single_cycle(
                goal_state=goal_state,
                observation=observation,
            )

            cycles += 1

            if result.get("status") != "completed":
                return {
                    "status": result.get("status", "failed"),
                    "goal": goal_state,
                    "cycles": cycles,
                    "cycle_count": self._cycle_count,
                    "max_cycles": max_cycles,
                    "reason": result.get("reason", "cycle_failed"),
                    "stopped": self._is_stopped(),
                    "last_cycle": result,
                }

        reason = (
            "max_cycles_reached"
            if cycles >= max_cycles
            else exhaustion_reason
        )

        return {
            "status": "completed",
            "goal": goal_state,
            "cycles": cycles,
            "cycle_count": self._cycle_count,
            "max_cycles": max_cycles,
            "reason": reason,
            "stopped": self._is_stopped(),
        }

    def _run_single_cycle(
        self,
        goal_state: dict,
        observation: Any,
    ) -> dict:
        """
        Execute exactly one cognitive cycle.
        """

        result = self.cognitive_engine.run_cycle(
            goal_state,
            observation,
        )

        if not isinstance(result, dict):
            raise TypeError(
                "cognitive_engine.run_cycle must return a dict"
            )

        self._cycle_count += 1
        self._history.append(result)

        return result

    def stop(self) -> None:
        """
        Stop the autonomous loop.
        """
        self._stopped = True

        stop = getattr(self.cognitive_engine, "stop", None)
        if callable(stop):
            stop()

    def reset(self) -> None:
        """
        Reset loop state and the underlying cognitive engine when
        supported.
        """
        self._stopped = False
        self._cycle_count = 0
        self._history.clear()

        reset = getattr(self.cognitive_engine, "reset", None)
        if callable(reset):
            reset()

    def get_history(self) -> list[dict]:
        """
        Return a copy of cycle history.
        """
        return list(self._history)

    def get_cycle_count(self) -> int:
        """
        Return completed cycle count.
        """
        return self._cycle_count

    def is_stopped(self) -> bool:
        """
        Return whether this autonomous loop is stopped.
        """
        return self._stopped

    def _is_stopped(self) -> bool:
        """
        Check both local and cognitive-engine stop state.
        """
        if self._stopped:
            return True

        return bool(self.cognitive_engine.is_stopped())

    @staticmethod
    def _validate_goal(goal_state: dict) -> None:
        """
        Validate goal state.
        """
        if not isinstance(goal_state, dict):
            raise TypeError("goal_state must be a dict")

        goal = goal_state.get("goal")

        if not isinstance(goal, str) or not goal.strip():
            raise ValueError("goal_state must contain a non-empty goal")

    @staticmethod
    def _validate_max_cycles(max_cycles: int) -> None:
        """
        Validate cycle limit.
        """
        if isinstance(max_cycles, bool):
            raise TypeError("max_cycles must be an integer")

        if not isinstance(max_cycles, int):
            raise TypeError("max_cycles must be an integer")

        if max_cycles <= 0:
            raise ValueError("max_cycles must be positive")

    @staticmethod
    def _validate_observations(
        observations: Iterable[Any],
    ) -> list[Any]:
        """
        Validate and materialize backward-compatible observations.
        """
        if observations is None:
            raise TypeError("observations cannot be None")

        if isinstance(observations, (str, bytes, bytearray)):
            raise TypeError(
                "observations must be an iterable of observations"
            )

        try:
            observation_list = list(observations)
        except TypeError as exc:
            raise TypeError(
                "observations must be an iterable"
            ) from exc

        return observation_list

    @staticmethod
    def _validate_observation_provider(provider) -> None:
        """
        Validate provider interface.
        """
        if provider is None:
            raise TypeError("observation_provider cannot be None")

        observe = getattr(provider, "observe", None)

        if not callable(observe):
            raise TypeError(
                "observation_provider must provide observe"
    )
