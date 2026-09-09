"""
Sudha AI - Perception Observation Provider

Version: 0.1

Connects the perception layer to the ObservationProvider
interface.

Flow:

External Input Source
        ↓
PerceptionObservationProvider
        ↓
PerceptionEngine
        ↓
Unified Observation
        ↓
ObservationProvider consumers

The provider does not invent observations.
The external source supplies the raw multimodal input.
PerceptionEngine converts that input into the canonical
observation structure used by downstream cognitive systems.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional

from core.observation_provider import ObservationProvider
from core.perception import PerceptionEngine


class PerceptionObservationProvider(ObservationProvider):
    """
    Observation provider backed by the PerceptionEngine.

    The source callable must return a dictionary containing
    one or more supported perception inputs:

        {
            "text": "...",
            "voice": ...,
            "image": ...,
            "video": ...
        }

    Only keys supported by PerceptionEngine are accepted.

    The provider does not create or infer missing observations.
    It only passes supplied input through the perception layer.
    """

    SUPPORTED_INPUTS = {
        "text",
        "voice",
        "image",
        "video",
    }

    def __init__(
        self,
        source: Callable[[], Dict[str, Any]],
        perception_engine: Optional[PerceptionEngine] = None,
    ) -> None:
        if not callable(source):
            raise TypeError("source must be callable")

        if perception_engine is not None and not isinstance(
            perception_engine,
            PerceptionEngine,
        ):
            raise TypeError(
                "perception_engine must be a PerceptionEngine"
            )

        super().__init__(source)

        self._perception_engine = (
            perception_engine
            if perception_engine is not None
            else PerceptionEngine()
        )

    def observe(self) -> Dict[str, Any]:
        """
        Obtain one raw multimodal input from the external source
        and convert it into one unified perception observation.

        The source is called exactly once per observation.

        Raises:
            TypeError:
                If the source does not return a dictionary.

            ValueError:
                If the source returns an unsupported input key,
                or supplies no supported input.
        """

        raw_input = self._source()

        if not isinstance(raw_input, dict):
            raise TypeError(
                "source must return a dictionary"
            )

        unsupported_inputs = set(raw_input) - self.SUPPORTED_INPUTS

        if unsupported_inputs:
            unsupported = sorted(unsupported_inputs)

            raise ValueError(
                "unsupported perception inputs: "
                f"{unsupported}"
            )

        if not raw_input:
            raise ValueError(
                "source returned no perception inputs"
            )

        return self._perceive_inputs(raw_input)

    def _perceive_inputs(
        self,
        raw_input: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convert supplied raw inputs into the canonical
        PerceptionEngine observation structure.

        Only inputs explicitly supplied by the source are passed
        to PerceptionEngine.
        """

        return self._perception_engine.create_multimodal_observation(
            text=raw_input.get("text"),
            voice=raw_input.get("voice"),
            image=raw_input.get("image"),
            video=raw_input.get("video"),
        )

    def reset(self) -> None:
        """
        Reset hook.

        The provider itself does not maintain an input iterator,
        so there is no internal state to reset.
        """
        return None

    def get_configuration(self) -> dict:
        """
        Return provider configuration.
        """

        return {
            "provider": self.__class__.__name__,
            "source_configured": True,
            "perception_engine": (
                self._perception_engine.__class__.__name__
            ),
            "supported_inputs": sorted(
                self.SUPPORTED_INPUTS
            ),
        }
