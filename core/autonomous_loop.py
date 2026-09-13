"""
Sudha AI - Autonomous Loop

Version 0.1 (Educational)

Yeh loop system ko repeatedly chalata hai:
    Observation → Prediction → Actual → Difference → Learning → Memory

Important limitations:
- Yeh infinite loop nahi chalta (max_cycles se bound hai)
- Actual outcome khud invent nahi karta
- Sirf diya gaya observation provider + actual provider use karta hai
- Real intelligence / knowledge generation nahi hai
"""

from __future__ import annotations

from typing import Any, Callable, Optional


class AutonomousLoop:
    """
    Bounded autonomous learning loop.

    Expects a learning engine that provides:
        run_cycle(observation, actual) -> dict
        is_stopped() -> bool
        (optional) stop()
        (optional) reset()
    """

    def __init__(self, learning_engine, max_cycles: int = 10):
        if learning_engine is None:
            raise ValueError("learning_engine is required")

        if not hasattr(learning_engine, "run_cycle") or not callable(learning_engine.run_cycle):
            raise TypeError("learning_engine must provide run_cycle method")

        if not hasattr(learning_engine, "is_stopped") or not callable(learning_engine.is_stopped):
            raise TypeError("learning_engine must provide is_stopped method")

        if not isinstance(max_cycles, int) or isinstance(max_cycles, bool):
            raise TypeError("max_cycles must be an integer")

        if max_cycles <= 0:
            raise ValueError("max_cycles must be positive")

        self.learning_engine = learning_engine
        self.max_cycles = max_cycles
        self._history: list[dict] = []
        self._cycle_count = 0
        self._stopped = False

    def run(
        self,
        observation_provider,
        actual_provider=None,
        max_cycles: Optional[int] = None,
    ) -> dict:
        """
        Run the autonomous loop.

        observation_provider: object with .observe() method
                              or a callable that returns next observation
        actual_provider:      object with .get_actual(observation) method
                              or a callable that returns actual for given observation
                              If None, actual = observation (simple demo mode)
        """
        if max_cycles is None:
            max_cycles = self.max_cycles

        if not isinstance(max_cycles, int) or isinstance(max_cycles, bool):
            raise TypeError("max_cycles must be an integer")

        if max_cycles <= 0:
            raise ValueError("max_cycles must be positive")

        self._validate_provider(observation_provider, "observation_provider")

        if self._is_stopped():
            return {
                "status": "stopped",
                "cycles": 0,
                "cycle_count": self._cycle_count,
                "max_cycles": max_cycles,
                "reason": "stopped_before_start",
                "stopped": True,
            }

        cycles = 0

        while cycles < max_cycles:
            if self._is_stopped():
                return {
                    "status": "stopped",
                    "cycles": cycles,
                    "cycle_count": self._cycle_count,
                    "max_cycles": max_cycles,
                    "reason": "stopped",
                    "stopped": True,
                    "history": list(self._history),
                }

            # Get next observation
            try:
                observation = self._get_observation(observation_provider)
            except StopIteration:
                return {
                    "status": "completed",
                    "cycles": cycles,
                    "cycle_count": self._cycle_count,
                    "max_cycles": max_cycles,
                    "reason": "observation_provider_exhausted",
                    "stopped": self._is_stopped(),
                    "history": list(self._history),
                }

            # Get actual outcome
            actual = self._get_actual(actual_provider, observation)

            # Run one learning cycle
            result = self.learning_engine.run_cycle(
                observation=observation,
                actual=actual,
            )

            if not isinstance(result, dict):
                return {
                    "status": "failed",
                    "cycles": cycles,
                    "cycle_count": self._cycle_count,
                    "max_cycles": max_cycles,
                    "reason": "invalid_cycle_result",
                    "last_result": result,
                }

            self._cycle_count += 1
            cycles += 1
            self._history.append(result)

            if result.get("status") not in ("learned", "completed", "predicted"):
                return {
                    "status": result.get("status", "failed"),
                    "cycles": cycles,
                    "cycle_count": self._cycle_count,
                    "max_cycles": max_cycles,
                    "reason": result.get("reason", "cycle_failed"),
                    "last_result": result,
                    "history": list(self._history),
                }

        return {
            "status": "completed",
            "cycles": cycles,
            "cycle_count": self._cycle_count,
            "max_cycles": max_cycles,
            "reason": "max_cycles_reached",
            "stopped": self._is_stopped(),
            "history": list(self._history),
        }

    def stop(self) -> dict:
        self._stopped = True
        if hasattr(self.learning_engine, "stop") and callable(self.learning_engine.stop):
            self.learning_engine.stop()
        return {
            "status": "stopped",
            "cycle_count": self._cycle_count,
        }

    def reset(self) -> dict:
        self._stopped = False
        self._cycle_count = 0
        self._history.clear()

        if hasattr(self.learning_engine, "reset") and callable(self.learning_engine.reset):
            self.learning_engine.reset()

        return {"status": "reset"}

    def get_history(self) -> list[dict]:
        return list(self._history)

    def get_cycle_count(self) -> int:
        return self._cycle_count

    def is_stopped(self) -> bool:
        return self._is_stopped()

    def _is_stopped(self) -> bool:
        if self._stopped:
            return True
        return bool(self.learning_engine.is_stopped())

    def _get_observation(self, provider) -> Any:
        if callable(provider) and not hasattr(provider, "observe"):
            return provider()
        return provider.observe()

    def _get_actual(self, provider, observation) -> Any:
        if provider is None:
            # Simple demo mode: actual = observation
            return observation

        if callable(provider) and not hasattr(provider, "get_actual"):
            return provider(observation)

        return provider.get_actual(observation)

    @staticmethod
    def _validate_provider(provider, name: str) -> None:
        if provider is None:
            raise ValueError(f"{name} is required")

        has_observe = hasattr(provider, "observe") and callable(provider.observe)
        is_callable = callable(provider)

        if not (has_observe or is_callable):
            raise TypeError(
                f"{name} must have an observe() method or be callable"
      )
