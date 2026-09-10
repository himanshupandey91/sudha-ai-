"""
Sudha AI - Experiment Loop Integration

Version 0.5

Connects:

Hypothesis
    ↓
Prediction
    ↓
Environment / Experiment
    ↓
Actual Observation
    ↓
Difference
    ↓
Learning
    ↓
Memory
    ↓
World Model

Version 0.5:
- Supports real Environment state transitions.
- Environment actions must be explicitly supplied.
- Supports an action_selector callback.
- Preserves legacy experiment support.
- Extracts actual observations explicitly.
- Prevents experiment metadata from entering learning calculations.
- No fake actual values.
- No uncontrolled infinite loops.
- No external side effects.
- Deterministic and testable.
"""

from core.closed_loop import ClosedLoopLearningEngine


class ExperimentLoopEngine:

    def __init__(
        self,
        closed_loop=None,
        experiment=None,
        environment=None,
        action=None,
        action_selector=None,
        max_cycles=10
    ):
        self.closed_loop = (
            closed_loop
            if closed_loop is not None
            else ClosedLoopLearningEngine(
                max_cycles=max_cycles
            )
        )

        self.experiment = experiment
        self.environment = environment
        self.action = action
        self.action_selector = action_selector

    def predict(
        self,
        observation,
        hypothesis=None
    ):
        """
        Generate a prediction while propagating
        the selected hypothesis.
        """

        try:
            return self.closed_loop.predict(
                observation,
                hypothesis=hypothesis
            )

        except TypeError:
            return self.closed_loop.predict(
                observation
            )

    def _extract_actual(self, result):
        """
        Extract the actual observed value.

        Supported forms:

        1. Direct numeric result:
           20

        2. Structured result:
           {
               "status": "experiment_completed",
               "actual": 20
           }

        3. Environment result:
           {
               "status": "completed",
               "action": "...",
               "before_state": {...},
               "after_state": {...},
               "actual": 21.0
           }
        """

        if isinstance(result, dict):

            if "actual" not in result:
                return {
                    "status": "failed",
                    "reason": "experiment_result_missing_actual"
                }

            return {
                "status": "actual_extracted",
                "actual": result["actual"]
            }

        if isinstance(result, (int, float)):

            return {
                "status": "actual_extracted",
                "actual": result
            }

        return {
            "status": "failed",
            "reason": "invalid_actual_result"
        }

    def _resolve_environment_action(
        self,
        observation,
        hypothesis=None
    ):
        """
        Resolve the action that will be executed
        by the Environment.

        Priority:

        1. action_selector(...)
        2. explicitly configured action
        3. unavailable

        No automatic hypothesis → action mapping is
        performed. This prevents the cognitive system
        from inventing an environmental meaning for
        a hypothesis.
        """

        if callable(self.action_selector):

            try:
                selected_action = self.action_selector(
                    observation=observation,
                    hypothesis=hypothesis
                )

            except TypeError:
                selected_action = self.action_selector(
                    observation,
                    hypothesis
                )

            return selected_action

        if self.action is not None:
            return self.action

        return None

    def _run_environment(
        self,
        observation,
        hypothesis=None
    ):
        """
        Execute one controlled Environment transition.
        """

        if self.environment is None:
            return {
                "status": "unavailable",
                "reason": "environment_not_configured"
            }

        step = getattr(
            self.environment,
            "step",
            None
        )

        if not callable(step):
            return {
                "status": "rejected",
                "reason": "invalid_environment"
            }

        selected_action = self._resolve_environment_action(
            observation=observation,
            hypothesis=hypothesis
        )

        if selected_action is None:
            return {
                "status": "unavailable",
                "reason": "environment_action_not_configured"
            }

        try:
            environment_result = step(
                selected_action
            )

        except Exception as error:

            return {
                "status": "failed",
                "reason": "environment_execution_failed",
                "error": str(error)
            }

        extraction = self._extract_actual(
            environment_result
        )

        if extraction["status"] != "actual_extracted":
            return extraction

        return {
            "status": "experiment_completed",
            "observation": observation,
            "hypothesis": hypothesis,
            "action": selected_action,
            "actual": extraction["actual"],
            "experiment_result": environment_result
        }

    def run_experiment(
        self,
        observation,
        hypothesis=None
    ):
        """
        Execute one actual experiment.

        Environment has priority when configured.
        Legacy Experiment support remains available.
        """

        if self.closed_loop.is_stopped():
            return {
                "status": "stopped",
                "reason": "closed_loop_stopped"
            }

        # Real Environment path.
        if self.environment is not None:

            return self._run_environment(
                observation=observation,
                hypothesis=hypothesis
            )

        # Legacy Experiment path.
        if self.experiment is None:
            return {
                "status": "unavailable",
                "reason": "experiment_not_configured"
            }

        execute = getattr(
            self.experiment,
            "run",
            None
        )

        if not callable(execute):
            return {
                "status": "rejected",
                "reason": "invalid_experiment"
            }

        try:

            if hypothesis is not None:

                try:
                    experiment_result = execute(
                        observation,
                        hypothesis=hypothesis
                    )

                except TypeError:
                    experiment_result = execute(
                        observation
                    )

            else:

                experiment_result = execute(
                    observation
                )

        except Exception as error:

            return {
                "status": "failed",
                "reason": "experiment_execution_failed",
                "error": str(error)
            }

        extraction = self._extract_actual(
            experiment_result
        )

        if extraction["status"] != "actual_extracted":
            return extraction

        return {
            "status": "experiment_completed",
            "observation": observation,
            "hypothesis": hypothesis,
            "actual": extraction["actual"],
            "experiment_result": experiment_result
        }

    def run_cycle(
        self,
        observation,
        hypothesis=None
    ):
        """
        Execute:

        prediction
            ↓
        actual experiment/environment
            ↓
        learning
        """

        prediction_result = self.predict(
            observation,
            hypothesis=hypothesis
        )

        if prediction_result["status"] != "predicted":
            return prediction_result

        experiment_result = self.run_experiment(
            observation=observation,
            hypothesis=hypothesis
        )

        if experiment_result["status"] != "experiment_completed":
            return experiment_result

        actual = experiment_result["actual"]

        learning_result = self.closed_loop.learn(
            observation=observation,
            prediction=prediction_result["prediction"],
            actual=actual
        )

        return {
            "status": "completed",
            "observation": observation,
            "hypothesis": hypothesis,
            "prediction": prediction_result["prediction"],
            "actual": actual,
            "difference": learning_result[
                "cycle"
            ]["difference"],
            "learning": learning_result[
                "cycle"
            ]["learning"],
            "world_model": learning_result[
                "cycle"
            ]["world_model"],
            "cycle": learning_result["cycle"],
            "stopped": learning_result["stopped"],
            "action": experiment_result.get(
                "action"
            ),
            "experiment_result": experiment_result.get(
                "experiment_result"
            )
        }

    def stop(self):
        return self.closed_loop.stop()

    def reset(self):
        return self.closed_loop.reset()

    def get_history(self):
        return self.closed_loop.get_history()

    def get_cycle_count(self):
        return self.closed_loop.get_cycle_count()

    def is_stopped(self):
        return self.closed_loop.is_stopped()
