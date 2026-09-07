"""
Sudha AI - Cognitive Experiment Engine

Version 0.6

Connects:

Goal
    ↓
Hypothesis Generation
    ↓
Hypothesis Selection
    ↓
Plan
    ↓
Selected Hypothesis
    ↓
Hypothesis-Specific Prediction
    ↓
Experiment
    ↓
Observed Result
    ↓
Prediction Error
    ↓
Hypothesis-Specific Prediction Learning
    ↓
Hypothesis Performance Learning
    ↓
Memory
    ↓
World Model
    ↓
Next Cycle

Version 0.6:
- Adds a real hypothesis-specific adaptive predictor.
- Connects PredictionEngine to AdaptivePredictor.
- Preserves legacy observation-based prediction behavior.
- Seeds the selected hypothesis with the prediction actually used.
- Updates the same selected hypothesis from the observed actual result.
- Keeps hypothesis attribution explicit.
- Keeps experiment results external to the predictor.
- Does not invent experiment results.
- Does not fake adaptation.
- Preserves bounded execution.
- No uncontrolled loops.
- No external side effects by itself.
- Fully testable.
"""

from core.hypothesis_planner import HypothesisPlanningEngine
from core.experiment_loop import ExperimentLoopEngine
from core.closed_loop import ClosedLoopLearningEngine
from core.prediction import PredictionEngine
from core.adaptive_predictor import AdaptivePredictor


class CognitiveExperimentEngine:

    def __init__(
        self,
        hypothesis_planner=None,
        experiment_loop=None
    ):
        self.hypothesis_planner = (
            hypothesis_planner
            if hypothesis_planner is not None
            else HypothesisPlanningEngine()
        )

        if experiment_loop is not None:

            self.experiment_loop = (
                experiment_loop
            )

        else:

            self.prediction_adaptive = (
                AdaptivePredictor(
                    learning_rate=0.5
                )
            )

            self.prediction_engine = (
                PredictionEngine(
                    adaptive_predictor=(
                        self.prediction_adaptive
                    )
                )
            )

            self.experiment_loop = (
                ExperimentLoopEngine(
                    closed_loop=(
                        ClosedLoopLearningEngine(
                            prediction_engine=(
                                self.prediction_engine
                            )
                        )
                    )
                )
            )

    def reason(self, goal_state):
        return self.hypothesis_planner.create_reasoning_plan(
            goal_state
        )

    def predict(
        self,
        observation,
        hypothesis=None
    ):
        """
        Generate a prediction using the selected hypothesis.

        Backward compatibility:
        - predict(observation)
        - predict(observation, hypothesis)
        """

        try:

            return self.experiment_loop.predict(
                observation,
                hypothesis=hypothesis
            )

        except TypeError:

            return self.experiment_loop.predict(
                observation
            )

    def run_experiment(
        self,
        observation,
        hypothesis=None
    ):
        return self.experiment_loop.run_experiment(
            observation=observation,
            hypothesis=hypothesis
        )

    def _get_prediction_engine(self):
        """
        Return the hypothesis-aware prediction engine
        when the configured experiment loop exposes one.
        """

        closed_loop = getattr(
            self.experiment_loop,
            "closed_loop",
            None
        )

        if closed_loop is None:
            return None

        prediction_engine = getattr(
            closed_loop,
            "prediction_engine",
            None
        )

        return prediction_engine

    def _seed_hypothesis_prediction(
        self,
        hypothesis_name,
        prediction
    ):
        """
        Seed the selected hypothesis with the exact
        prediction that was actually used.

        This is important because the first observed
        actual result must be compared against the
        prediction that produced the experiment.

        The seed is only created when no hypothesis-
        specific prediction exists yet.
        """

        prediction_engine = (
            self._get_prediction_engine()
        )

        if prediction_engine is None:
            return {
                "status": "unavailable",
                "reason": "prediction_engine_not_configured"
            }

        adaptive_predictor = getattr(
            prediction_engine,
            "adaptive_predictor",
            None
        )

        if adaptive_predictor is None:
            return {
                "status": "unavailable",
                "reason": "adaptive_predictor_not_configured"
            }

        predictor = getattr(
            adaptive_predictor,
            "predict",
            None
        )

        seeder = getattr(
            adaptive_predictor,
            "set_prediction",
            None
        )

        if not callable(predictor):
            return {
                "status": "failed",
                "reason": "adaptive_predictor_invalid"
            }

        if not callable(seeder):
            return {
                "status": "failed",
                "reason": "adaptive_predictor_cannot_seed"
            }

        existing = predictor(
            hypothesis_name
        )

        if existing is None:

            return seeder(
                hypothesis_name,
                prediction
            )

        return {
            "status": "existing",
            "hypothesis": hypothesis_name,
            "prediction": existing
        }

    def _learn_hypothesis_prediction(
        self,
        hypothesis_name,
        actual
    ):
        """
        Update the same hypothesis-specific predictor
        from the observed actual result.
        """

        prediction_engine = (
            self._get_prediction_engine()
        )

        if prediction_engine is None:
            return {
                "status": "unavailable",
                "reason": "prediction_engine_not_configured"
            }

        learner = getattr(
            prediction_engine,
            "learn",
            None
        )

        if not callable(learner):
            learner = getattr(
                prediction_engine,
                "update_from_actual",
                None
            )

        if not callable(learner):
            return {
                "status": "unavailable",
                "reason": "prediction_learning_not_configured"
            }

        return learner(
            hypothesis_name,
            actual
        )

    def run_cycle(
        self,
        goal_state,
        observation
    ):
        reasoning = self.reason(
            goal_state
        )

        if reasoning["status"] != "ready":
            return reasoning

        selected_hypothesis = reasoning[
            "selected_hypothesis"
        ]

        hypothesis_name = selected_hypothesis.get(
            "hypothesis"
        )

        if not isinstance(
            hypothesis_name,
            str
        ) or not hypothesis_name:

            return {
                "status": "failed",
                "reason": "invalid_selected_hypothesis"
            }

        prediction = self.predict(
            observation,
            hypothesis=selected_hypothesis
        )

        if prediction["status"] != "predicted":
            return prediction

        used_prediction = prediction[
            "prediction"
        ]

        seed_result = (
            self._seed_hypothesis_prediction(
                hypothesis_name,
                used_prediction
            )
        )

        if seed_result["status"] in (
            "failed",
        ):

            return seed_result

        experiment_result = self.run_experiment(
            observation=observation,
            hypothesis=selected_hypothesis
        )

        if experiment_result["status"] != "experiment_completed":
            return experiment_result

        actual = experiment_result[
            "actual"
        ]

        learning_result = (
            self.experiment_loop.closed_loop.learn(
                observation=observation,
                prediction=used_prediction,
                actual=actual
            )
        )

        if learning_result["status"] != "learned":
            return learning_result

        difference = learning_result[
            "cycle"
        ]["difference"]

        hypothesis_prediction_learning = (
            self._learn_hypothesis_prediction(
                hypothesis_name,
                actual
            )
        )

        if hypothesis_prediction_learning[
            "status"
        ] == "failed":

            return {
                "status": "failed",
                "reason": (
                    "hypothesis_prediction_learning_failed"
                ),
                "error": hypothesis_prediction_learning.get(
                    "error"
                )
            }

        hypothesis_learning = (
            self.hypothesis_planner.record_result(
                hypothesis=hypothesis_name,
                difference=difference
            )
        )

        return {
            "status": "completed",
            "goal": goal_state.get("goal"),
            "hypotheses": reasoning["hypotheses"],
            "selected_hypothesis": selected_hypothesis,
            "plan": reasoning["plan"],
            "observation": observation,
            "prediction": used_prediction,
            "actual": actual,
            "difference": difference,
            "learning": learning_result[
                "cycle"
            ]["learning"],
            "world_model": learning_result[
                "cycle"
            ]["world_model"],
            "hypothesis_prediction_learning": (
                hypothesis_prediction_learning
            ),
            "hypothesis_learning": (
                hypothesis_learning
            ),
            "cycle": learning_result[
                "cycle"
            ],
            "stopped": learning_result[
                "stopped"
            ]
        }

    def stop(self):
        return self.experiment_loop.stop()

    def reset(self):
        return self.experiment_loop.reset()

    def get_history(self):
        return self.experiment_loop.get_history()

    def get_cycle_count(self):
        return self.experiment_loop.get_cycle_count()

    def is_stopped(self):
        return self.experiment_loop.is_stopped()

    def get_learned_hypotheses(self):
        return self.hypothesis_planner.get_learned_hypotheses()

    def clear_learning(self):
        return self.hypothesis_planner.clear_learning()

    def get_configuration(self):
        configuration = {
            "hypothesis_planner": type(
                self.hypothesis_planner
            ).__name__,
            "experiment_loop": type(
                self.experiment_loop
            ).__name__
        }

        prediction_engine = (
            self._get_prediction_engine()
        )

        configuration[
            "prediction_engine"
        ] = (
            type(
                prediction_engine
            ).__name__
            if prediction_engine is not None
            else None
        )

        adaptive_predictor = (
            getattr(
                prediction_engine,
                "adaptive_predictor",
                None
            )
            if prediction_engine is not None
            else None
        )

        configuration[
            "adaptive_predictor"
        ] = (
            type(
                adaptive_predictor
            ).__name__
            if adaptive_predictor is not None
            else None
        )

        return configuration
