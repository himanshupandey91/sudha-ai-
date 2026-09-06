"""
Sudha AI - Adaptive Cognitive Cycle

Version 0.1

Adaptive reasoning cycle:

Observation
    ↓
Prediction
    ↓
Hypothesis
    ↓
Experiment
    ↓
Actual Result
    ↓
Difference
    ↓
Evaluation
    ↓
Learning
    ↓
Next Cycle

This module is intentionally isolated from the
existing CognitiveLoop so existing behavior remains stable.
"""


class AdaptiveCognitiveCycle:

    def __init__(
        self,
        cognitive_experiment=None,
        max_cycles=10
    ):
        if not isinstance(max_cycles, int):
            raise ValueError(
                "max_cycles must be an integer"
            )

        if max_cycles <= 0:
            raise ValueError(
                "max_cycles must be greater than zero"
            )

        self.cognitive_experiment = (
            cognitive_experiment
        )

        self.max_cycles = max_cycles
        self.history = []
        self.stopped = False

    def stop(self):
        """
        Stop future cycles.
        """
        self.stopped = True

    def reset(self):
        """
        Reset the cycle controller.
        """
        self.stopped = False

    def is_stopped(self):
        return self.stopped

    def clear_history(self):
        self.history.clear()

    def run_cycle(
        self,
        goal=None,
        context=None
    ):
        """
        Execute one adaptive cognitive cycle.

        The experiment engine is responsible for
        producing the actual reasoning/experiment result.

        No fake outcome is generated here.
        """

        if self.stopped:
            return {
                "status": "stopped",
                "reason": "stop_requested"
            }

        if self.cognitive_experiment is None:
            return {
                "status": "unavailable",
                "reason": "cognitive_experiment_not_configured"
            }

        try:
            result = self.cognitive_experiment.reason(
                goal or {},
                context or {}
            )

        except Exception as error:
            return {
                "status": "failed",
                "reason": "cognitive_experiment_error",
                "error": str(error)
            }

        if not isinstance(result, dict):
            return {
                "status": "failed",
                "reason": "invalid_cycle_result"
            }

        self.history.append(result)

        return result

    def run(
        self,
        goal=None,
        context=None
    ):
        """
        Run a bounded adaptive cognitive cycle.

        Stops when:
        - max_cycles is reached
        - stop() is requested
        - a cycle fails
        """

        self.reset()

        results = []

        for cycle in range(
            1,
            self.max_cycles + 1
        ):

            if self.is_stopped():
                return {
                    "status": "stopped",
                    "cycles_completed": len(results),
                    "results": results
                }

            result = self.run_cycle(
                goal=goal,
                context=context
            )

            result["cycle"] = cycle

            results.append(result)

            if result.get("status") not in (
                "completed",
                "ready"
            ):
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
            "cognitive_experiment": (
                type(
                    self.cognitive_experiment
                ).__name__
                if self.cognitive_experiment is not None
                else None
            ),
            "max_cycles": self.max_cycles,
            "stopped": self.stopped,
            "history_size": len(self.history)
        }
