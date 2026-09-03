"""
Sudha AI - Experiment Manager

Version 0.6.0

Controls the experimentation process.

Flow:

Goal
→ Hypothesis
→ Simulation
→ Evaluation
→ Learning
→ Selection
→ Next Experiment
→ Repeat

Version 0.6.0:
- Interruptible stop control
- Thread-safe stop signal
- Maximum experiment safety guard
- Experiment status tracking
- Asynchronous experimentation support
- Evaluation Engine integration
- Evaluation history
- Best result tracking
- Evaluation-based hypothesis selection
- Initial exploration of all hypotheses
- Best-hypothesis exploitation after exploration
- Experiment Learning Engine integration
- Learning history
- Learned hypothesis performance

Important:
- Every available hypothesis is explored once first.
- Every valid evaluation is passed to the learning engine.
- Selection remains deterministic.
- The simulation engine remains isolated from external side effects.

Safety:
- Explicit stop control
- Maximum experiment guard
- No arbitrary code execution
- No external side effects
"""


import threading

from core.evaluation import EvaluationEngine
from core.experiment_learning import ExperimentLearningEngine


class ExperimentManager:

    def __init__(
        self,
        hypothesis_engine,
        simulation_engine,
        max_experiments=10,
        evaluation_engine=None,
        learning_engine=None
    ):
        """
        Initialize the Experiment Manager.
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

        if learning_engine is None:
            learning_engine = ExperimentLearningEngine()

        self.learning_engine = learning_engine

        self.running = False
        self.stop_requested = False

        self.experiment_count = 0

        self.results = []
        self.evaluations = []

        self.best_result = None
        self.best_evaluation = None

        self.explored_hypotheses = []

        self.stop_event = threading.Event()

        self.worker_thread = None

    def start(self, goal_state, state=None):
        """
        Run the experimentation loop synchronously.

        Phase 1:
            Explore every available hypothesis once.

        Phase 2:
            Select the best evaluated hypothesis
            and continue exploiting it.

        The loop stops when:

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

                hypothesis_data = self._select_hypothesis(
                    hypotheses
                )

                if hypothesis_data is None:
                    break

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

                    self._record_explored_hypothesis(
                        hypothesis
                    )

                    self._learn_from_evaluation(
                        evaluation
                    )

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
            "best_evaluation": self.best_evaluation,
            "explored_hypotheses": list(
                self.explored_hypotheses
            ),
            "learning": {
                "records": self.learning_engine.retrieve_all(),
                "record_count": self.learning_engine.size(),
                "best_hypothesis": (
                    self.learning_engine.best_hypothesis()
                ),
                "hypothesis_performance": (
                    self.learning_engine.hypothesis_performance()
                )
            }
        }

    def get_learning_status(self):
        """
        Return the current learning state.
        """

        return {
            "records": self.learning_engine.retrieve_all(),
            "record_count": self.learning_engine.size(),
            "best_hypothesis": (
                self.learning_engine.best_hypothesis()
            ),
            "hypothesis_performance": (
                self.learning_engine.hypothesis_performance()
            )
        }

    def _reset_run_state(self):
        """
        Reset per-run experiment state.

        Learning history is intentionally preserved
        across runs.
        """

        self.running = False
        self.stop_requested = False

        self.experiment_count = 0

        self.results = []
        self.evaluations = []

        self.best_result = None
        self.best_evaluation = None

        self.explored_hypotheses = []

        self.stop_event.clear()

    def _select_hypothesis(self, hypotheses):
        """
        Select the next hypothesis.

        Exploration phase:
            Select the first hypothesis that has
            not been tested yet in this run.

        Exploitation phase:
            Prefer the best hypothesis learned
            across all completed experiments.

        Fallback:
            Use the best evaluation from the
            current run.

        This allows learning to influence
        future experimentation while keeping
        the selection deterministic.
        """

        if not isinstance(hypotheses, list):
            return None

        if not hypotheses:
            return None

        for hypothesis_data in hypotheses:

            hypothesis = hypothesis_data.get(
                "hypothesis"
            )

            if hypothesis not in self.explored_hypotheses:
                return hypothesis_data

        learned_best = (
            self.learning_engine.best_hypothesis()
        )

        if learned_best is not None:

            for hypothesis_data in hypotheses:

                if hypothesis_data.get(
                    "hypothesis"
                ) == learned_best:

                    return hypothesis_data

        if self.best_evaluation is not None:

            best_hypothesis = self.best_evaluation.get(
                "hypothesis"
            )

            for hypothesis_data in hypotheses:

                if hypothesis_data.get(
                    "hypothesis"
                ) == best_hypothesis:

                    return hypothesis_data

        return hypotheses[0]

    def _record_explored_hypothesis(
        self,
        hypothesis
    ):
        """
        Record a hypothesis after successful evaluation.
        """

        if hypothesis not in self.explored_hypotheses:

            self.explored_hypotheses.append(
                hypothesis
            )

    def _learn_from_evaluation(
        self,
        evaluation
    ):
        """
        Send a valid evaluation to the
        Experiment Learning Engine.
        """

        return self.learning_engine.learn(
            evaluation
        )

    def _update_best_result(
        self,
        experiment_result,
        evaluation
    ):
        """
        Keep the experiment with the best evaluation.
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
        """

        predicted_difference = result.get(
            "predicted_difference"
        )

        return predicted_difference == 0
