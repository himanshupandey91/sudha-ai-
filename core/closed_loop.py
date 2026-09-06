"""
Sudha AI - Closed Loop Learning Engine

Version 0.1

Learning cycle:

Prediction
    ↓
Experiment
    ↓
Actual Result
    ↓
Difference
    ↓
Learning
    ↓
Memory
    ↓
World Model
    ↓
Next Prediction

This version provides a controlled foundation
for repeated learning cycles.

Safety:
- Explicit maximum cycle limit
- No uncontrolled infinite loop
- No external side effects
- Deterministic behavior
"""

from core.experience_learning import ExperienceLearningEngine


class ClosedLoopLearningEngine:

    def __init__(
        self,
        experience_learning=None,
        max_cycles=10
    ):
        if not isinstance(max_cycles, int):
            raise TypeError("max_cycles must be an integer")

        if max_cycles <= 0:
            raise ValueError("max_cycles must be greater than zero")

        self.experience_learning = (
            experience_learning
            if experience_learning is not None
            else ExperienceLearningEngine()
        )

        self.max_cycles = max_cycles
        self.cycle_count = 0
        self.stopped = False
        self.history = []

    def predict(self, observation):
        if self.stopped:
            return {
                "status": "stopped",
                "reason": "closed_loop_stopped"
            }

        return self.experience_learning.predict(observation)

    def learn(self, observation, prediction, actual):
        if self.stopped:
            return {
                "status": "stopped",
                "reason": "closed_loop_stopped"
            }

        result = self.experience_learning.learn(
            observation=observation,
            prediction=prediction,
            actual=actual
        )

        self.cycle_count += 1

        cycle = {
            "cycle": self.cycle_count,
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": result["difference"],
            "learning": result["learning"],
            "world_model": result["world_model"]
        }

        self.history.append(dict(cycle))

        if self.cycle_count >= self.max_cycles:
            self.stopped = True

        return {
            "status": "learned",
            "cycle": cycle,
            "stopped": self.stopped
        }

    def run_cycle(self, observation, actual):
        if self.stopped:
            return {
                "status": "stopped",
                "reason": "closed_loop_stopped"
            }

        prediction_result = self.predict(observation)

        if prediction_result["status"] != "predicted":
            return prediction_result

        prediction = prediction_result["prediction"]

        return self.learn(
            observation=observation,
            prediction=prediction,
            actual=actual
        )

    def stop(self):
        self.stopped = True

        return {
            "status": "stopped",
            "cycle_count": self.cycle_count
        }

    def reset(self):
        self.cycle_count = 0
        self.stopped = False
        self.history.clear()

        return {
            "status": "reset"
        }

    def get_history(self):
        return [
            dict(cycle)
            for cycle in self.history
        ]

    def get_cycle_count(self):
        return self.cycle_count

    def is_stopped(self):
        return self.stopped

    def get_configuration(self):
        return {
            "max_cycles": self.max_cycles,
            "cycle_count": self.cycle_count,
            "stopped": self.stopped
        }
