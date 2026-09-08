"""
Sudha AI - Observation Provider

Version: 0.1

Provides a small, explicit interface for obtaining observations
from an external environment.

The provider does not invent observations.
It obtains them from a caller-supplied source.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable, Iterator


class ObservationProvider:
    """
    Generic observation provider.

    The source callable is responsible for obtaining an observation
    from the real environment, sensor, simulator, camera, API, etc.

    No observation is generated internally.
    """

    def __init__(self, source: Callable[[], Any]):
        if not callable(source):
            raise TypeError("source must be callable")

        self._source = source

    def observe(self) -> Any:
        """
        Obtain exactly one observation from the external source.
        """
        return self._source()

    def reset(self) -> None:
        """
        Reset hook for providers that need resetting.

        The generic provider has no internal state, so this is a no-op.
        """
        return None

    def get_configuration(self) -> dict:
        """
        Return provider configuration.
        """
        return {
            "provider": self.__class__.__name__,
            "source_configured": True,
        }


class SequenceObservationProvider(ObservationProvider):
    """
    Deterministic finite provider used for testing and controlled
    experiments.

    This is an adapter around an existing iterable. It does not
    pretend that the sequence is a real-world sensor.
    """

    def __init__(self, observations: Iterable[Any]):
        if observations is None:
            raise TypeError("observations cannot be None")

        self._observations = list(observations)
        self._iterator: Iterator[Any] = iter(self._observations)

    def observe(self) -> Any:
        """
        Return the next supplied observation.

        Raises:
            StopIteration: when the supplied sequence is exhausted.
        """
        return next(self._iterator)

    def reset(self) -> None:
        """
        Restart the finite observation sequence.
        """
        self._iterator = iter(self._observations)

    def get_configuration(self) -> dict:
        """
        Return provider configuration.
        """
        return {
            "provider": self.__class__.__name__,
            "source_configured": True,
            "observation_count": len(self._observations),
        }
