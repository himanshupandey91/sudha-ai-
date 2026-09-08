"""
Sudha AI - Cognitive Experiment Engine

Version 0.8

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

Version 0.8:
- Integrates ExecutiveReasoningEngine.
- Includes learned hypotheses that are not present in the
  current static hypothesis list.
- Preserves learned hypothesis metadata such as:
    - learned
    - score
    - average_error
    - attempts
    - exploration
- Executive reasoning evaluates real available evidence.
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

            self.experiment_loop = experiment_loop

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
        Generate hypotheses, create a planning result, and then
        apply executive reasoning using all available evidence.

        If executive reasoning cannot resolve a decision,
        the hypothesis planner's own selection is preserved.

        Learned hypotheses that are not part of the current static
        candidate list are also exposed to executive reasoning.
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

            selected_hypothesis = (
                self._find_learned_hypothesis(
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
        Convert planner hypotheses and learned hypotheses
        into the evidence format required by
        ExecutiveReasoningEngine.

        Two sources are considered:

        1. Current static hypotheses.
        2. Previously learned hypotheses.

        A learned hypothesis is included even when it is not
        present in the current static candidate list.

        No evidence is invented.
        """

        if not isinstance(
            hypotheses,
            (list, tuple)
        ):
            return []

        candidates_by_name = {}

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

            priority = hypothesis.get(
                "priority"
            )

            if isinstance(
                priority,
                (int, float)
            ) and not isinstance(
                priority,
                bool
            ):
                candidate[
                    "priority"
                ] = float(priority)

            candidates_by_name[
                hypothesis_name
            ] = candidate

        hypothesis_learning = getattr(
            self.hypothesis_planner,
            "hypothesis_learning",
            None
        )

        if hypothesis_learning is None:
            return list(
                candidates_by_name.values()
            )

        rank = getattr(
            hypothesis_learning,
            "rank",
            None
        )

        if not callable(rank):
            return list(
                candidates_by_name.values()
            )

        learned_records = rank()

        if not isinstance(
            learned_records,
            (list, tuple)
        ):
            learned_records = []

        for learned in learned_records:

            if not isinstance(
                learned,
                dict
            ):
                continue

            hypothesis_name = (
                learned.get(
                    "hypothesis"
                )
            )

            if not isinstance(
                hypothesis_name,
                str
            ):
                continue

            candidate = candidates_by_name.get(
                hypothesis_name,
                {
                    "name": hypothesis_name,
                    "priority": 0
                }
            )

            average_error = (
                learned.get(
                    "average_error"
                )
            )

            score = learned.get(
                "score"
            )

            attempts = learned.get(
                "attempts"
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
                ] = float(score)

            if isinstance(
                attempts,
                int
            ) and not isinstance(
                attempts,
                bool
            ):
                candidate[
                    "attempts"
                ] = attempts

            candidate[
                "learned"
            ] = True

            candidate[
                "exploration"
            ] = False

            candidates_by_name[
                hypothesis_name
            ] = candidate

        return list(
            candidates_by_name.values()
        )

    def _find_hypothesis(
        self,
        hypotheses,
        hypothesis_name
    ):
        """
        Find the actual planner hypothesis.

        If the hypothesis has learned performance data,
        merge that data into the returned hypothesis so
        downstream components receive the complete learned
        state.
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
            ) != hypothesis_name:
                continue

            selected = dict(
                hypothesis
            )

            learned = (
                self._get_learned_record(
                    hypothesis_name
                )
            )

            if learned is not None:

                selected[
                    "learned"
                ] = True

                selected[
                    "score"
                ] = learned.get(
                    "score"
                )

                selected[
                    "average_error"
                ] = learned.get(
                    "average_error"
                )

                selected[
                    "attempts"
                ] = learned.get(
                    "attempts"
                )

                selected[
                    "exploration"
                ] = False

            else:

                selected.setdefault(
                    "learned",
                    False
                )

                selected.setdefault(
                    "exploration",
                    False
                )

            return selected

        return None

    def _find_learned_hypothesis(
        self,
        hypothesis_name
    ):
        """
        Reconstruct a learned hypothesis that may not exist
        in the current static hypothesis list.

        Such a hypothesis is valid because its evidence comes
        directly from HypothesisLearningEngine.
        """

        learned = (
            self._get_learned_record(
                hypothesis_name
            )
        )

        if learned is None:
            return None

        return {
            "hypothesis": hypothesis_name,
            "priority": 0,
            "learned": True,
            "exploration": False,
            "score": learned.get(
                "score"
            ),
            "average_error": learned.get(
                "average_error"
            ),
            "attempts": learned.get(
                "attempts"
            )
        }

    def _get_learned_record(
        self,
        hypothesis_name
    ):
        """
        Return the real learned record for a hypothesis.

        Returns None when no learning evidence exists.
        """

        hypothesis_learning = getattr(
            self.hypothesis_planner,
            "hypothesis_learning",
            None
        )

        if hypothesis_learning is None:
            return None

        evaluate = getattr(
            hypothesis_learning,
            "evaluate",
            None
        )

        if not callable(evaluate):
            return None

        result = evaluate(
            hypothesis_name
        )

        if not isinstance(
            result,
            dict
        ):
            return None

        if result.get(
            "status"
        ) == "unseen":
            return None

        return result

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

        if seed_result["status"] == "failed":
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

        closed_loop = getattr(
            self.experiment_loop,
            "closed_loop",
            None
        )

        if closed_loop is None:
            return {
                "status": "failed",
                "reason": "closed_loop_not_configured"
            }

        learning_result = (
            closed_loop.learn(
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
     
