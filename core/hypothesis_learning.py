"""
Sudha AI - Hypothesis Learning Engine

Version 0.1

Learns which hypotheses perform better from
observed experiment outcomes.

Flow:

Hypothesis
    ↓
Experiment Result
    ↓
Prediction Error
    ↓
Performance Score
    ↓
Hypothesis Update

Design goals:
- Deterministic behavior
- Explicit hypothesis performance tracking
- Bounded state
- No external side effects
- Fully testable
"""


class HypothesisLearningEngine:

    def __init__(self):
        self._records = {}

    def record(
        self,
        hypothesis,
        difference
    ):
        if not isinstance(hypothesis, str):
            raise TypeError(
                "hypothesis must be a string"
            )

        if not hypothesis:
            raise ValueError(
                "hypothesis cannot be empty"
            )

        if not isinstance(
            difference,
            (int, float)
        ):
            raise TypeError(
                "difference must be a number"
            )

        record = self._records.setdefault(
            hypothesis,
            {
                "hypothesis": hypothesis,
                "attempts": 0,
                "total_error": 0,
                "average_error": 0,
                "score": 0
            }
        )

        record["attempts"] += 1
        record["total_error"] += difference

        record["average_error"] = (
            record["total_error"]
            / record["attempts"]
        )

        record["score"] = (
            1
            / (1 + record["average_error"])
        )

        return {
            "status": "recorded",
            "hypothesis": hypothesis,
            "attempts": record["attempts"],
            "average_error": record[
                "average_error"
            ],
            "score": record["score"]
        }

    def evaluate(self, hypothesis):
        if not isinstance(hypothesis, str):
            raise TypeError(
                "hypothesis must be a string"
            )

        record = self._records.get(
            hypothesis
        )

        if record is None:
            return {
                "status": "unseen",
                "hypothesis": hypothesis,
                "attempts": 0,
                "average_error": None,
                "score": 0
            }

        return dict(record)

    def rank(self):
        records = [
            dict(record)
            for record in self._records.values()
        ]

        records.sort(
            key=lambda item: (
                item["score"],
                -item["average_error"]
            ),
            reverse=True
        )

        return records

    def best(self):
        ranked = self.rank()

        if not ranked:
            return None

        return dict(ranked[0])

    def get_records(self):
        return [
            dict(record)
            for record in self._records.values()
        ]

    def clear(self):
        self._records.clear()

        return {
            "status": "cleared",
            "count": 0
        }

    def size(self):
        return len(self._records)

    def get_configuration(self):
        return {
            "hypothesis_count": len(
                self._records
            )
        }
