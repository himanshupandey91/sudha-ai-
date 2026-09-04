"""
Sudha AI - Experiment Learning Engine

Version 0.3

Learns from completed experiment evaluations
and maintains performance statistics for each hypothesis.

Design goals:
- Deterministic learning
- Explicit learning records
- Hypothesis performance tracking
- Success and partial outcome tracking
- Bounded history
- Reliable hypothesis selection
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

        The record contains:
        - hypothesis
        - predicted_difference
        - outcome

        Valid records are retained in bounded memory.
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
        for every hypothesis.
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
                or difference < performance[hypothesis]
            ):
                performance[hypothesis] = difference

        return performance

    def hypothesis_statistics(self):
        """
        Return detailed statistics for every hypothesis.

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

    def select_best_hypothesis(self):
        """
        Select the best hypothesis using observed performance.

        Selection priority:

        1. Lowest average predicted difference.
        2. If tied, lowest best predicted difference.
        3. If still tied, earliest hypothesis encountered.

        Returns:
            Hypothesis name or None.
        """

        statistics = self.hypothesis_statistics()

        if not statistics:
            return None

        best_hypothesis = None
        best_key = None

        for hypothesis, data in statistics.items():

            selection_key = (
                data["average"],
                data["best"]
            )

            if (
                best_key is None
                or selection_key < best_key
            ):
                best_key = selection_key
                best_hypothesis = hypothesis

        return best_hypothesis

    def get_hypothesis_statistics(
        self,
        hypothesis
    ):
        """
        Return statistics for one hypothesis.

        Returns None if the hypothesis has
        never been evaluated.
        """

        if not isinstance(hypothesis, str):
            raise TypeError(
                "hypothesis must be a string"
            )

        statistics = self.hypothesis_statistics()

        data = statistics.get(
            hypothesis
        )

        if data is None:
            return None

        return data.copy()

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
