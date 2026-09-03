"""
Sudha AI - Experiment Manager

Version 0.4.0

Controls the experimentation process.

Flow:

Goal
→ Hypothesis
→ Simulation
→ Evaluation
→ Best Result
→ Repeat

Version 0.4.0:
- Interruptible stop control
- Thread-safe stop signal
- Maximum experiment safety guard
- Experiment status tracking
- Complete stop response
- Asynchronous experimentation support
- Evaluation Engine integration
- Evaluation history
- Best evaluation tracking

Important:
- Hypothesis selection is still round-robin in this version.
- Evaluation-based hypothesis selection will be added
  in a later version.

Safety:
- Explicit stop control
- Maximum experiment guard
- No arbitrary code execution
- No external side effects
- Deterministic behavior
"""


import threading

from core.evaluation import EvaluationEngine


class ExperimentManager:

    def __init__(
        self,
        hypothesis_engine,
        simulation_engine,
        max_experiments=10,
        evaluation_engine=None
    ):
        """
        Initialize the Experiment Manager.

        max_experiments:
            Maximum number of experiments allowed
            in one run.

        evaluation_engine:
            Optional EvaluationEngine instance.

            If none is supplied, the manager creates
            its own EvaluationEngine.
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

        if evaluation_engine is None:
            evaluation_engine = EvaluationEngine()

        self.evaluation_engine = evaluation_engine

        self.running = False
        self.stop_requested = False

        self.experiment_count = 0

        self.results = []
        self.evaluations = []

        self.best_result = None
        self.best_evaluation = None

        self.stop_event = threading.Event()

        self.worker_thread = None

    def start(self, goal_state, state=None):
        """
        Run the experimentation loop synchronously.

        The loop continues until:

        1. A solution is found.
        2. stop() is requested.
        3. max_experiments is reached.
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

        self._reset_run_state()

        self.running = True

        try:

            while self.running:

                if self.stop_event.is_set():
                    self.stop_requested = True
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

                evaluation = self.evaluation_engine.evaluate(
                    experiment_result
                )

                experiment_result["evaluation"] = evaluation

                self.evaluations.append(
                    evaluation
                )

                if evaluation.get("status") == "evaluated":
                    self._update_best_result(
                        experiment_result,
                        evaluation
                    )

                if self._is_solution(result):
                    break

        finally:

            self.running = False

        return self.get_status()

    def start_async(self, goal_state, state=None):
        """
        Start experimentation in a background thread.

        This allows stop() to be called while the
        experimentation loop is running.

        Returns:
            The worker thread.
        """

        if self.running:
            return {
                "status": "already_running"
            }

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

        self.worker_thread = threading.Thread(
            target=self.start,
            args=(goal_state, state),
            daemon=True
        )

        self.worker_thread.start()

        return self.worker_thread

    def stop(self):
        """
        Request the experimentation loop to stop.

        The currently running experiment is allowed
        to finish.

        The next loop check stops further
        experimentation.
        """

        self.stop_requested = True
        self.stop_event.set()

        return {
            "status": "stopped",
            "stop_requested": True,
            "running": self.running,
            "experiment_count": self.experiment_count
        }

    def wait(self, timeout=None):
        """
        Wait for the background experimentation thread
        to finish.

        timeout:
            Maximum number of seconds to wait.

        Returns:
            True if the worker finished.
            False if it is still running.
        """

        if self.worker_thread is None:
            return True

        self.worker_thread.join(
            timeout=timeout
        )

        return not self.worker_thread.is_alive()

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
            "evaluations": list(self.evaluations),
            "best_result": self.best_result,
            "best_evaluation": self.best_evaluation
        }

    def _reset_run_state(self):
        """
        Reset state before starting a new run.
        """

        self.running = False
        self.stop_requested = False

        self.experiment_count = 0

        self.results = []
        self.evaluations = []

        self.best_result = None
        self.best_evaluation = None

        self.stop_event.clear()

    def _update_best_result(
        self,
        experiment_result,
        evaluation
    ):
        """
        Keep the experiment with the best evaluation.

        Lower predicted difference means
        better expected performance.
        """

        if self.best_evaluation is None:

            self.best_result = experiment_result
            self.best_evaluation = evaluation

            return

        if self.evaluation_engine.better(
            evaluation,
            self.best_evaluation
        ):

            self.best_result = experiment_result
            self.best_evaluation = evaluation

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
