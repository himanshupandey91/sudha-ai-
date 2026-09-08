"""
Sudha AI - Cognitive Experiment Engine

Version 0.7

Connects:

Goal
    ↓
Hypothesis Generation
    ↓
Hypothesis Planning
    ↓
Executive Reasoning
    ↓
Selected Decision
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

Version 0.7:
- Integrates ExecutiveReasoningEngine.
- Executive reasoning evaluates available hypothesis evidence.
- The executive decision determines the hypothesis used downstream.
- Preserves hypothesis-specific adaptive prediction.
- Preserves hypothesis performance learning.
- Preserves legacy observation-based prediction behavior.
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
from core.executive_reasoning import ExecutiveReasoningEngine


class CognitiveExperimentEngine:

    def __init__(
        self,
        hypothesis_planner=None,
        experiment_loop=None,
        executive_reasoning=None
    ):
        self.hypothesis_planner = (
            hypothesis_planner
            if hypothesis_planner is not None
            else HypothesisPlanningEngine()
        )

        self.executive_reasoning = (
            executive_reasoning
            if executive_reasoning is not None
            else ExecutiveReasoningEngine()
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
        """
        Generate hypotheses and create a planning result.

        Executive reasoning is applied after hypothesis planning
        so that the final selected hypothesis is evidence-driven.

        If executive reasoning cannot resolve a decision, the
        hypothesis planner's selection is preserved as fallback.
        """

        planning = (
            self.hypothesis_planner.create_reasoning_plan(
                goal_state
            )
        )

        if planning.get("status") != "ready":
            return planning

        hypotheses = planning.get(
            "hypotheses",
            []
        )

        executive_candidates = (
            self._build_executive_candidates(
                hypotheses
            )
        )

        if not executive_candidates:
            return planning

        executive_result = (
            self.executive_reasoning.reason(
                executive_candidates
            )
        )

        if executive_result.get(
            "status"
        ) != "decision_selected":

            return {
                **planning,
                "executive_reasoning": (
                    executive_result
                )
            }

        selected_name = (
            executive_result[
                "decision"
            ].get(
                "selected"
            )
        )

        selected_hypothesis = (
            self._find_hypothesis(
                hypotheses,
                selected_name
            )
        )

        if selected_hypothesis is None:
            return {
                **planning,
                "executive_reasoning": (
                    executive_result
                )
            }

        selected_hypothesis = dict(
            selected_hypothesis
        )

        selected_hypothesis[
            "executive_selected"
        ] = True

        return {
            **planning,
            "selected_hypothesis": (
                selected_hypothesis
            ),
            "executive_reasoning": (
                executive_result
            )
        }

    def _build_executive_candidates(
        self,
        hypotheses
    ):
        """
        Convert planner hypotheses into the evidence format
        required by ExecutiveReasoningEngine.

        Learned hypothesis performance is used when available.

        No evidence is invented:
        - known average_error is passed through
        - known score is passed through
        - otherwise the candidate remains unresolved
        """

        if not isinstance(
            hypotheses,
            (list, tuple)
        ):
            return []

        candidates = []

        for hypothesis in hypotheses:

            if not isinstance(
                hypothesis,
                dict
            ):
                continue

            hypothesis_name = (
                hypothesis.get(
                    "hypothesis"
                )
            )

            if not isinstance(
                hypothesis_name,
                str
            ):
                continue

            candidate = {
                "name": hypothesis_name
            }

            learned = (
                self.hypothesis_planner
                .hypothesis_learning
                .evaluate(
                    hypothesis_name
                )
            )

            if learned.get(
                "status"
            ) != "unseen":

                average_error = (
                    learned.get(
                        "average_error"
                    )
                )

                score = learned.get(
                    "score"
                )

                if isinstance(
                    average_error,
                    (int, float)
                ) and not isinstance(
                    average_error,
                    bool
                ):
                    candidate[
                        "average_error"
                    ] = float(
                        average_error
                    )

                if isinstance(
                    score,
                    (int, float)
                ) and not isinstance(
                    score,
                    bool
                ):
                    candidate[
                        "score"
                    ] = float(
                        score
                    )

            candidates.append(
                candidate
            )

        return candidates

    def _find_hypothesis(
        self,
        hypotheses,
        hypothesis_name
    ):
        """
        Find the actual planner hypothesis selected by
        ExecutiveReasoningEngine.
        """

        if not isinstance(
            hypothesis_name,
            str
        ):
            return None

        for hypothesis in hypotheses:

            if not isinstance(
                hypothesis,
                dict
            ):
                continue

            if hypothesis.get(
                "hypothesis"
            ) == hypothesis_name:

                return hypothesis

        return None

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
            "executive_reasoning": reasoning.get(
                "executive_reasoning"
            ),
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
            "executive_reasoning": type(
                self.executive_reasoning
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
