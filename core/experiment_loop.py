"""
Sudha AI - Experiment Loop Integration

Version 0.4

Connects:

Hypothesis
    ↓
Hypothesis-Aware Prediction
    ↓
Experiment
    ↓
Observed Result
    ↓
Actual Value Extraction
    ↓
Difference
    ↓
Learning
    ↓
Memory
    ↓
World Model

Version 0.4:
- Propagates hypothesis into prediction.
- Supports hypothesis-aware prediction engines.
- Preserves legacy predictors.
- Supports hypothesis-aware experiments.
- Preserves legacy experiments.
- Normalizes structured experiment results.
- Extracts the actual observed value explicitly.
- Prevents experiment metadata from entering the learning calculation.
- Controlled experiment execution.
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
        Extract the actual observed value from an
        experiment result.

        Supported forms:

        1. Direct numeric result:
           20

        2. Structured result:
           {
               "status": "experiment_completed",
               "actual": 20
           }

        Legacy experiments returning numeric values
        remain supported.
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

    def run_experiment(
        self,
        observation,
        hypothesis=None
    ):
        if self.closed_loop.is_stopped():
            return {
                "status": "stopped",
                "reason": "closed_loop_stopped"
            }

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
            "stopped": learning_result["stopped"]
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
