"""
Sudha AI - Cognitive Loop

Version 0.2

Closed adaptive cognitive cycle:

Observation
    ↓
Prediction
    ↓
Hypothesis / Experiment Engine
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
- backward compatible with the existing pipeline API
"""

from threading import Event

from core.cognitive_pipeline import CognitivePipeline


class CognitiveLoop:

    def __init__(
        self,
        pipeline=None,
        experiment_engine=None,
        max_cycles=10
    ):
        self.pipeline = (
            pipeline
            if pipeline is not None
            else CognitivePipeline()
        )

        self.experiment_engine = experiment_engine

        if not isinstance(max_cycles, int):
            raise ValueError("max_cycles must be an integer")

        if max_cycles <= 0:
            raise ValueError("max_cycles must be greater than zero")

        self.max_cycles = max_cycles
        self.stop_event = Event()
        self.history = []

    def stop(self):
        """
        Request the loop to stop.
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

        Existing behavior is preserved:
            Observation
                ↓
            Prediction
                ↓
            Actual
                ↓
            Difference
                ↓
            Learning
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

        The existing pipeline remains the default execution path.

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

    def run_experiment_cycle(
        self,
        goal=None,
        context=None
    ):
        """
        Execute one cycle through an external
        CognitiveExperimentEngine.

        This method is intentionally separate from
        run_cycle() so the existing API remains stable.

        The experiment engine must provide:

            reason(goal, context)

        or:

            run(goal, context)

        No fake actual result is generated here.
        """

        if self.is_stopped():
            return {
                "status": "stopped",
                "reason": "stop_requested"
            }

        if self.experiment_engine is None:
            return {
                "status": "unavailable",
                "reason": "experiment_engine_not_configured"
            }

        try:
            if hasattr(self.experiment_engine, "reason"):
                result = self.experiment_engine.reason(
                    goal or {},
                    context or {}
                )

            elif hasattr(self.experiment_engine, "run"):
                result = self.experiment_engine.run(
                    goal=goal or {},
                    context=context or {}
                )

            else:
                return {
                    "status": "failed",
                    "reason": "experiment_engine_interface_missing"
                }

        except Exception as error:
            return {
                "status": "failed",
                "reason": "experiment_engine_error",
                "error": str(error)
            }

        if not isinstance(result, dict):
            return {
                "status": "failed",
                "reason": "experiment_engine_returned_invalid_result"
            }

        self.history.append(result)

        return result

    def get_history(self):
        return list(self.history)

    def get_configuration(self):
        return {
            "pipeline": type(
                self.pipeline
            ).__name__,
            "experiment_engine": (
                type(self.experiment_engine).__name__
                if self.experiment_engine is not None
                else None
            ),
            "max_cycles": self.max_cycles,
            "stopped": self.is_stopped(),
            "history_size": len(self.history)
        }
