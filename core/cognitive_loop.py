"""
Sudha AI - Cognitive Loop

Version 0.1

Closed cognitive cycle:

Observation
    ↓
Prediction
    ↓
Actual Outcome
    ↓
Difference
    ↓
Learning
    ↓
Next Cycle

Safety:
- bounded cycles
- explicit stop()
- no uncontrolled infinite loop
- no external side effects
"""

from threading import Event

from core.cognitive_pipeline import CognitivePipeline


class CognitiveLoop:

    def __init__(
        self,
        pipeline=None,
        max_cycles=10
    ):
        self.pipeline = (
            pipeline
            if pipeline is not None
            else CognitivePipeline()
        )

        if not isinstance(max_cycles, int):
            raise ValueError("max_cycles must be an integer")

        if max_cycles <= 0:
            raise ValueError("max_cycles must be greater than zero")

        self.max_cycles = max_cycles
        self.stop_event = Event()
        self.history = []

    def stop(self):
        """
        Immediately request the loop to stop.
        """
        self.stop_event.set()

    def reset_stop(self):
        """
        Allow the loop to run again.
        """
        self.stop_event.clear()

    def is_stopped(self):
        return self.stop_event.is_set()

    def clear_history(self):
        self.history.clear()

    def run_cycle(
        self,
        actual,
        text=None,
        voice=None,
        image=None,
        video=None
    ):
        """
        Execute one complete cognitive cycle.
        """

        if self.is_stopped():
            return {
                "status": "stopped",
                "reason": "stop_requested"
            }

        result = self.pipeline.run_with_actual(
            actual=actual,
            text=text,
            voice=voice,
            image=image,
            video=video
        )

        self.history.append(result)

        return result

    def run(
        self,
        actual,
        text=None,
        voice=None,
        image=None,
        video=None
    ):
        """
        Run bounded repeated cognitive cycles.

        The loop stops when:
        1. max_cycles is reached
        2. stop() is called
        3. a cycle fails
        """

        self.reset_stop()

        results = []

        for cycle in range(1, self.max_cycles + 1):

            if self.is_stopped():
                return {
                    "status": "stopped",
                    "cycles_completed": len(results),
                    "results": results
                }

            result = self.run_cycle(
                actual=actual,
                text=text,
                voice=voice,
                image=image,
                video=video
            )

            result["cycle"] = cycle

            results.append(result)

            if result.get("status") != "completed":
                return {
                    "status": "failed",
                    "cycles_completed": len(results),
                    "results": results
                }

        return {
            "status": "completed",
            "cycles_completed": len(results),
            "max_cycles": self.max_cycles,
            "results": results
        }

    def get_history(self):
        return list(self.history)

    def get_configuration(self):
        return {
            "pipeline": type(self.pipeline).__name__,
            "max_cycles": self.max_cycles,
            "stopped": self.is_stopped(),
            "history_size": len(self.history)
        }
