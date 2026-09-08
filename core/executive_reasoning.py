"""
Sudha AI - Executive Reasoning Engine

Version 0.1

Purpose:
    Evaluate candidate hypotheses using available evidence and
    select a decision without inventing experimental outcomes.

Design principles:
    - Deterministic
    - Explainable
    - Bounded
    - No hidden side effects
    - No fake learning
    - No invented observations
    - Compatible with hypothesis-planning systems
"""


class ExecutiveReasoningEngine:
    """
    Executive layer responsible for evaluating candidate hypotheses
    and selecting a bounded decision.

    The engine does not execute actions or experiments.
    It only reasons over information that is explicitly supplied.
    """

    def __init__(self, exploration=False):
        if not isinstance(exploration, bool):
            raise TypeError("exploration must be a boolean")

        self.exploration = exploration
        self.history = []

    def _validate_hypothesis(self, hypothesis):
        if not isinstance(hypothesis, dict):
            raise TypeError("hypothesis must be a dictionary")

        name = hypothesis.get("name")

        if not isinstance(name, str):
            raise ValueError("hypothesis name must be a string")

        if not name.strip():
            raise ValueError("hypothesis name cannot be empty")

        return hypothesis

    def _validate_hypotheses(self, hypotheses):
        if not isinstance(hypotheses, (list, tuple)):
            raise TypeError("hypotheses must be a list or tuple")

        validated = []

        for hypothesis in hypotheses:
            validated.append(
                self._validate_hypothesis(hypothesis)
            )

        if not validated:
            raise ValueError("hypotheses cannot be empty")

        return validated

    def _extract_error(self, hypothesis):
        """
        Extract the currently available prediction error.

        Supported fields:
            average_error
            error
            prediction_error

        Missing error is represented by None rather than invented.
        """

        for field in (
            "average_error",
            "error",
            "prediction_error",
        ):
            value = hypothesis.get(field)

            if isinstance(value, bool):
                continue

            if isinstance(value, (int, float)):
                return float(value)

        return None

    def _extract_score(self, hypothesis):
        """
        Extract an optional hypothesis score.

        A score is only used when explicitly supplied.
        """

        score = hypothesis.get("score")

        if isinstance(score, bool):
            return None

        if isinstance(score, (int, float)):
            return float(score)

        return None

    def evaluate_hypothesis(self, hypothesis):
        """
        Evaluate one hypothesis using only supplied evidence.

        Lower prediction error is preferred.

        If prediction error is unavailable, an explicitly supplied
        score may be used.

        If neither is available, the hypothesis remains unresolved.
        """

        hypothesis = self._validate_hypothesis(hypothesis)

        error = self._extract_error(hypothesis)
        score = self._extract_score(hypothesis)

        if error is not None:
            return {
                "name": hypothesis["name"],
                "status": "evaluated",
                "criterion": "prediction_error",
                "error": error,
                "score": score,
            }

        if score is not None:
            return {
                "name": hypothesis["name"],
                "status": "evaluated",
                "criterion": "score",
                "error": None,
                "score": score,
            }

        return {
            "name": hypothesis["name"],
            "status": "unresolved",
            "criterion": None,
            "error": None,
            "score": None,
        }

    def evaluate(self, hypotheses):
        """
        Evaluate all supplied hypotheses.
        """

        hypotheses = self._validate_hypotheses(hypotheses)

        evaluations = [
            self.evaluate_hypothesis(hypothesis)
            for hypothesis in hypotheses
        ]

        return {
            "status": "evaluated",
            "evaluations": evaluations,
        }

    def _select_by_error(self, evaluations):
        candidates = [
            evaluation
            for evaluation in evaluations
            if evaluation["error"] is not None
        ]

        if not candidates:
            return None

        return min(
            candidates,
            key=lambda evaluation: evaluation["error"]
        )

    def _select_by_score(self, evaluations):
        candidates = [
            evaluation
            for evaluation in evaluations
            if evaluation["score"] is not None
        ]

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda evaluation: evaluation["score"]
        )

    def select_decision(self, evaluations):
        """
        Select one decision from evaluated hypotheses.

        Priority:
            1. Lowest prediction error
            2. Highest explicitly supplied score
            3. First unresolved hypothesis

        Exploration does not invent evidence. When enabled and no
        evidence-based winner exists, the first unresolved candidate
        is selected for bounded exploration.
        """

        if not isinstance(evaluations, (list, tuple)):
            raise TypeError("evaluations must be a list or tuple")

        if not evaluations:
            raise ValueError("evaluations cannot be empty")

        selected = self._select_by_error(evaluations)

        if selected is None:
            selected = self._select_by_score(evaluations)

        if selected is None:
            unresolved = [
                evaluation
                for evaluation in evaluations
                if evaluation["status"] == "unresolved"
            ]

            if self.exploration and unresolved:
                selected = unresolved[0]

        if selected is None:
            return {
                "status": "no_decision",
                "reason": "insufficient_evidence",
                "selected": None,
            }

        decision = {
            "status": "decision_selected",
            "selected": selected["name"],
            "criterion": (
                selected["criterion"]
                if selected["criterion"] is not None
                else "exploration"
            ),
            "error": selected["error"],
            "score": selected["score"],
        }

        self.history.append(decision)

        return decision

    def reason(self, hypotheses):
        """
        Complete executive reasoning pass.
        """

        evaluation = self.evaluate(hypotheses)

        decision = self.select_decision(
            evaluation["evaluations"]
        )

        return {
            "status": decision["status"],
            "evaluation": evaluation,
            "decision": decision,
        }

    def get_history(self):
        """
        Return a copy of executive decision history.
        """

        return list(self.history)

    def clear_history(self):
        """
        Clear decision history.
        """

        self.history.clear()

        return {
            "status": "cleared",
        }

    def get_configuration(self):
        return {
            "engine": type(self).__name__,
            "exploration": self.exploration,
            "history_size": len(self.history),
      }
