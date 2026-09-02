"""
Sudha AI - Experiment Manager

Version 0.2

Controls the continuous experimentation process.

Flow:

Goal
→ Hypothesis
→ Simulation
→ Evaluation
→ Next Experiment
→ Repeat

Safety:
- Explicit stop control
- Maximum experiment guard
- No arbitrary code execution
- No external side effects
- Deterministic behavior
"""


class ExperimentManager:

    def __init__(
        self,
        hypothesis_engine,
        simulation_engine,
        max_experiments=10
    ):
        """
        Initialize the Experiment Manager.

        max_experiments:
            Maximum number of experiments allowed
            in one run.
        """

        if not isinstance(max_experiments, int):
            raise TypeError(
                "max_experiments must be an integer"
            )

        if max_experiments <= 0:
            raise ValueError(
                "max_experiments must be greater than zero"
            )

        self.hypothesis_engine = hypothesis_engine
        self.simulation_engine = simulation_engine
        self.max_experiments = max_experiments

        self.running = False
        self.stop_requested = False
        self.experiment_count = 0
        self.results = []
        self.best_result = None

    def start(self, goal_state, state=None):
        """
        Start the continuous experimentation loop.

        The loop continues until:

        1. A solution is found.
        2. stop() is requested.
        3. max_experiments is reached.

        The same goal can generate another experiment
        after the available hypotheses have been tested.
        """

        if not isinstance(goal_state, dict):
            raise TypeError(
                "goal_state must be a dictionary"
            )

        if state is None:
            state = {}

        if not isinstance(state, dict):
            raise TypeError(
                "state must be a dictionary"
            )

        self.running = True
        self.stop_requested = False
        self.experiment_count = 0
        self.results = []
        self.best_result = None

        while self.running:

            if self.stop_requested:
                break

            if self.experiment_count >= self.max_experiments:
                break

            hypotheses = self.hypothesis_engine.generate(
                goal_state
            )

            if not hypotheses:
                break

            hypothesis_index = (
                self.experiment_count
                % len(hypotheses)
            )

            hypothesis_data = hypotheses[
                hypothesis_index
            ]

            hypothesis = hypothesis_data[
                "hypothesis"
            ]

            result = self.simulation_engine.simulate(
                hypothesis,
                state
            )

            self.experiment_count += 1

            experiment_result = {
                "experiment": self.experiment_count,
                "hypothesis": hypothesis,
                "result": result
            }

            self.results.append(
                experiment_result
            )

            if result.get("status") != "completed":
                continue

            self._update_best_result(
                experiment_result
            )

            if self._is_solution(result):
                break

        self.running = False

        return self.get_status()

    def stop(self):
        """
        Request the experimentation loop to stop.
        """

        self.stop_requested = True
        self.running = False

        return {
            "status": "stopped",
            "experiment_count": self.experiment_count
        }

    def is_running(self):
        """
        Return whether the experiment loop is running.
        """

        return self.running

    def get_status(self):
        """
        Return the current experiment status.
        """

        return {
            "running": self.running,
            "stop_requested": self.stop_requested,
            "experiment_count": self.experiment_count,
            "results": list(self.results),
            "best_result": self.best_result
        }

    def _update_best_result(self, experiment_result):
        """
        Keep the experiment with the lowest
        predicted prediction error.
        """

        result = experiment_result["result"]

        predicted_difference = result.get(
            "predicted_difference"
        )

        if not isinstance(
            predicted_difference,
            (int, float)
        ):
            return

        if self.best_result is None:
            self.best_result = experiment_result
            return

        current_best = self.best_result[
            "result"
        ].get(
            "predicted_difference"
        )

        if not isinstance(
            current_best,
            (int, float)
        ):
            self.best_result = experiment_result
            return

        if predicted_difference < current_best:
            self.best_result = experiment_result

    def _is_solution(self, result):
        """
        Determine whether the simulation result
        is good enough to stop experimentation.

        A predicted difference of zero means that
        the simulation predicts no remaining error.
        """

        predicted_difference = result.get(
            "predicted_difference"
        )

        return predicted_difference == 0
