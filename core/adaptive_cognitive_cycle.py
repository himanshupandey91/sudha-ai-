"""
Sudha AI - Adaptive Cognitive Cycle

Version 0.4

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
Feedback
    ↓
Next Cycle

Version 0.4:
- Supports CognitiveExperimentEngine.run_cycle(goal, observation)
- Preserves reason(goal, context) compatibility
- Carries previous cycle feedback into the next real cycle
- Keeps the original observation stable
- Allows the cognitive experiment to adapt across cycles
- Bounded cycles
- Explicit stop()
- No uncontrolled infinite loop
- No fake experiment result generation
- No external side effects by itself
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
        self.stopped = True

        return {
            "status": "stopped"
        }

    def reset(self):
        self.stopped = False

        return {
            "status": "reset"
        }

    def is_stopped(self):
        return self.stopped

    def clear_history(self):
        self.history.clear()

        return {
            "status": "cleared"
        }

    def _extract_observation(self, context):
        """
        Extract the stable observation used by the
        real cognitive experiment.

        Supported forms:

        context = {
            "observation": {...}
        }

        or:

        context = {
            ...
        }

        In the second form the complete context
        becomes the observation.
        """

        if not isinstance(context, dict):
            return context

        if "observation" in context:
            return context["observation"]

        return context

    def _build_cycle_context(
        self,
        context,
        previous_result
    ):
        """
        Build context for the next adaptive cycle.

        The original observation remains unchanged.

        Previous cycle feedback is added separately
        so the cognitive experiment can use the result
        of the previous cycle.
        """

        if not isinstance(context, dict):
            if previous_result is None:
                return context

            return {
                "observation": context,
                "previous_result": previous_result
            }

        cycle_context = dict(context)

        if previous_result is not None:
            cycle_context[
                "previous_result"
            ] = previous_result

        return cycle_context

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
                "cognitive_experiment.reason "
                "is not callable"
            )

        try:
            return reason(
                goal,
                context
            )

        except TypeError:
            return reason(
                goal
            )

    def _run_real_cycle(
        self,
        goal,
        context
    ):
        """
        Execute the real CognitiveExperimentEngine
        adaptive cycle.

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
        context=None,
        previous_result=None
    ):
        """
        Execute one adaptive cognitive cycle.

        Preferred path:

            CognitiveExperimentEngine.run_cycle()

        Compatibility path:

            reason(goal, context)
            or
            reason(goal)

        previous_result is optional and is used only
        to provide feedback to compatible reasoning
        systems.
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

        if goal is None:
            goal = {}

        if context is None:
            context = {}

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

                reasoning_context = (
                    self._build_cycle_context(
                        context,
                        previous_result
                    )
                )

                result = self._reason(
                    goal,
                    reasoning_context
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

        self.history.append(
            dict(result)
        )

        return result

    def run(
        self,
        goal=None,
        context=None
    ):
        """
        Run a bounded adaptive cognitive cycle.

        Each real cycle uses the same observation,
        while the underlying CognitiveExperimentEngine
        retains learned state.

        The previous result is also carried forward
        as feedback for compatible reasoning systems.

        The loop stops when:

        - max_cycles is reached
        - stop() is requested
        - a cycle fails
        """

        self.reset()

        results = []

        previous_result = None

        for cycle in range(
            1,
            self.max_cycles + 1
        ):

            if self.is_stopped():

                return {
                    "status": "stopped",
                    "cycles_completed": len(
                        results
                    ),
                    "results": results
                }

            cycle_context = (
                self._build_cycle_context(
                    context,
                    previous_result
                )
            )

            result = self.run_cycle(
                goal=goal,
                context=cycle_context,
                previous_result=previous_result
            )

            result = dict(result)

            result["cycle"] = cycle

            results.append(
                result
            )

            previous_result = dict(
                result
            )

            if result.get("status") not in (
                "completed",
                "ready"
            ):

                return {
                    "status": "failed",
                    "cycles_completed": len(
                        results
                    ),
                    "results": results
                }

        return {
            "status": "completed",
            "cycles_completed": len(results),
            "max_cycles": self.max_cycles,
            "results": results
        }

    def get_history(self):
        return [
            dict(result)
            for result in self.history
        ]

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
            "history_size": len(
                self.history
            )
    }
