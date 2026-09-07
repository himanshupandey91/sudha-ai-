"""
Sudha AI - Hypothesis Experiment Environment

Version 0.1

Controlled validation environment for hypothesis-aware experiments.

Purpose:
- Accept a selected hypothesis.
- Produce a deterministic observed result from that hypothesis.
- Allow the cognitive system to measure prediction error.
- Make hypothesis performance measurable across repeated cycles.

This is a controlled validation environment, not an external-world
experiment and not a claim of general intelligence.
"""


class HypothesisExperiment:

    def __init__(self, outcomes=None):
        if outcomes is None:
            outcomes = {
                "use_recent_experience": 5,
                "explore_new_pattern": 8,
                "use_world_model": 3,
            }

        if not isinstance(outcomes, dict):
            raise ValueError("outcomes must be a dictionary")

        if not outcomes:
            raise ValueError("outcomes must not be empty")

        for hypothesis, outcome in outcomes.items():
            if not isinstance(hypothesis, str):
                raise ValueError("hypothesis names must be strings")

            if not hypothesis:
                raise ValueError("hypothesis names must not be empty")

            if not isinstance(outcome, (int, float)):
                raise ValueError("outcomes must be numeric")

        self.outcomes = dict(outcomes)
        self.history = []

    def run(self, observation, hypothesis=None):
        if hypothesis is None:
            return {
                "status": "failed",
                "reason": "hypothesis_required",
            }

        if not isinstance(hypothesis, dict):
            return {
                "status": "failed",
                "reason": "invalid_hypothesis",
            }

        name = hypothesis.get("hypothesis")

        if name not in self.outcomes:
            return {
                "status": "failed",
                "reason": "unknown_hypothesis",
                "hypothesis": name,
            }

        actual = self.outcomes[name]

        result = {
            "status": "experiment_completed",
            "observation": observation,
            "hypothesis": hypothesis,
            "actual": actual,
        }

        self.history.append(result)

        return result

    def get_history(self):
        return list(self.history)

    def clear_history(self):
        self.history.clear()

    def get_outcomes(self):
        return dict(self.outcomes)

    def get_configuration(self):
        return {
            "hypotheses": list(self.outcomes.keys()),
            "history_size": len(self.history),
        }
