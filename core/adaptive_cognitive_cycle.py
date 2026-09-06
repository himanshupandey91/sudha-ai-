"""
Sudha AI - Adaptive Cognitive Cycle

Version 0.3

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
Memory
    ↓
World Model
    ↓
Hypothesis Update
    ↓
Next Cycle

The controller supports:
- CognitiveExperimentEngine.run_cycle(goal, observation)
- reason(goal, context)
- reason(goal)

Safety:
- bounded cycles
- explicit stop()
- no uncontrolled infinite loop
- no fake experiment result generation
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

        self.cognitive_experiment = cognitive_experiment
        self.max_cycles = max_cycles
        self.history = []
        self.stopped = False

    def stop(self):
        self.stopped = True

    def reset(self):
        self.stopped = False

    def is_stopped(self):
        return self.stopped

    def clear_history(self):
        self.history.clear()

    def _extract_observation(self, context):
        """
        Extract the observation used by the real
        cognitive experiment cycle.

        Supported forms:

        context = {
            "observation": {...}
        }

        or:

        context = {
            ...
        }

        In the second form the complete context is
        treated as the observation.
        """

        if not isinstance(context, dict):
            return context

        if "observation" in context:
            return context["observation"]

        return context

    def _reason(self, goal, context):
        """
        Backward-compatible reasoning interface.

        Supports:
        - reason(goal, context)
        - reason(goal)
        """

        reason = getattr(
            self.cognitive_experiment,
            "reason",
            None
        )

        if not callable(reason):
            raise AttributeError(
                "cognitive_experiment.reason is not callable"
            )

        try:
            return reason(goal, context)

        except TypeError:
            return reason(goal)

    def _run_real_cycle(self, goal, context):
        """
        Execute the real CognitiveExperimentEngine
        adaptive cycle when run_cycle() is available.

        Expected interface:

            run_cycle(
                goal_state,
                observation
            )
        """

        run_cycle = getattr(
            self.cognitive_experiment,
            "run_cycle",
            None
        )

        if not callable(run_cycle):
            return None

        observation = self._extract_observation(
            context
        )

        return run_cycle(
            goal,
            observation
        )

    def run_cycle(
        self,
        goal=None,
        context=None
    ):
        """
        Execute one adaptive cognitive cycle.

        Preferred path:
            CognitiveExperimentEngine.run_cycle()

        Compatibility path:
            reason(goal, context)
            or
            reason(goal)
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

        goal = goal or {}
        context = context or {}

        try:
            run_cycle = getattr(
                self.cognitive_experiment,
                "run_cycle",
                None
            )

            if callable(run_cycle):
                result = self._run_real_cycle(
                    goal,
                    context
                )
            else:
                result = self._reason(
                    goal,
                    context
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

        The loop stops when:
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
