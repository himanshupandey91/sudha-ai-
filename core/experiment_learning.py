"""
Sudha AI - Experiment Learning Engine

Version 0.2

Learns from completed experiment evaluations
and tracks performance statistics for each hypothesis.

Design goals:
- Deterministic learning
- Explicit learning records
- Track successful hypotheses
- Track partial results
- Track hypothesis performance
- Bounded history
- No external side effects
- Fully testable
"""


class ExperimentLearningEngine:

    def __init__(self, max_records=1000):
        """
        Initialize experiment learning.

        max_records:
            Maximum number of learning records retained.
        """

        if not isinstance(max_records, int):
            raise TypeError(
                "max_records must be an integer"
            )

        if max_records <= 0:
            raise ValueError(
                "max_records must be greater than zero"
            )

        self.max_records = max_records
        self.records = []

    def learn(self, evaluation):
        """
        Convert an evaluation into a learning record.

        Also updates the performance statistics
        for the evaluated hypothesis.
        """

        if not isinstance(evaluation, dict):
            raise TypeError(
                "evaluation must be a dictionary"
            )

        if evaluation.get("status") != "evaluated":
            return {
                "status": "rejected",
                "reason": "evaluation_not_valid"
            }

        hypothesis = evaluation.get(
            "hypothesis"
        )

        predicted_difference = evaluation.get(
            "predicted_difference"
        )

        if not isinstance(hypothesis, str):
            return {
                "status": "rejected",
                "reason": "hypothesis_must_be_a_string"
            }

        if not isinstance(
            predicted_difference,
            (int, float)
        ):
            return {
                "status": "rejected",
                "reason": "predicted_difference_must_be_numeric"
            }

        if predicted_difference == 0:
            outcome = "success"

        else:
            outcome = "partial"

        record = {
            "hypothesis": hypothesis,
            "predicted_difference": predicted_difference,
            "outcome": outcome
        }

        self.records.append(
            record
        )

        if len(self.records) > self.max_records:
            self.records.pop(0)

        return {
            "status": "learned",
            "record": record.copy(),
            "record_count": len(self.records)
        }

    def retrieve_all(self):
        """
        Return all learning records.
        """

        return [
            record.copy()
            for record in self.records
        ]

    def best_hypothesis(self):
        """
        Return the hypothesis with the lowest
        observed predicted difference.

        Returns:
            Hypothesis name or None.
        """

        if not self.records:
            return None

        best_record = min(
            self.records,
            key=lambda record: record[
                "predicted_difference"
            ]
        )

        return best_record["hypothesis"]

    def hypothesis_performance(self):
        """
        Return the best observed performance
        for each hypothesis.
        """

        performance = {}

        for record in self.records:

            hypothesis = record[
                "hypothesis"
            ]

            difference = record[
                "predicted_difference"
            ]

            if (
                hypothesis not in performance
                or difference
                < performance[hypothesis]
            ):
                performance[hypothesis] = difference

        return performance

    def hypothesis_statistics(self):
        """
        Return detailed performance statistics
        for every hypothesis.

        Statistics include:

        - tests
        - best
        - average
        - latest
        - success
        - partial
        """

        statistics = {}

        for record in self.records:

            hypothesis = record[
                "hypothesis"
            ]

            difference = record[
                "predicted_difference"
            ]

            outcome = record[
                "outcome"
            ]

            if hypothesis not in statistics:

                statistics[hypothesis] = {
                    "tests": 0,
                    "best": difference,
                    "average": 0,
                    "latest": difference,
                    "success": 0,
                    "partial": 0
                }

            data = statistics[
                hypothesis
            ]

            data["tests"] += 1

            if difference < data["best"]:
                data["best"] = difference

            data["latest"] = difference

            if outcome == "success":
                data["success"] += 1

            elif outcome == "partial":
                data["partial"] += 1

        for hypothesis, data in statistics.items():

            values = [
                record["predicted_difference"]
                for record in self.records
                if record["hypothesis"] == hypothesis
            ]

            data["average"] = (
                sum(values) / len(values)
            )

        return statistics

    def size(self):
        """
        Return the number of learning records.
        """

        return len(self.records)

    def clear(self):
        """
        Clear all learning records.
        """

        self.records.clear()

        return {
            "status": "cleared",
            "record_count": 0
        }
