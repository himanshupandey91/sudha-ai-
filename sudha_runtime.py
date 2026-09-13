from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import json
import time


@dataclass
class CycleResult:
    cycle: int
    observation: Any
    prediction: Any
    action: Any
    actual: Any
    error: float
    learning_applied: bool
    timestamp: float


class SudhaRuntime:
    """
    Real closed-loop runtime:

        observe
          ↓
        predict
          ↓
        act
          ↓
        observe result
          ↓
        calculate error
          ↓
        update predictor
          ↓
        save memory
          ↓
        next cycle
    """

    def __init__(
        self,
        environment,
        predictor,
        action_engine,
        memory=None,
        persistence_path="sudha_runtime_memory.json",
    ):
        self.environment = environment
        self.predictor = predictor
        self.action_engine = action_engine
        self.memory = memory
        self.persistence_path = persistence_path

        self.cycle_count = 0
        self.history = []

    def _calculate_error(self, prediction, actual) -> float:
        """
        Generic numeric prediction error.
        """
        try:
            return abs(float(actual) - float(prediction))
        except (TypeError, ValueError):
            return 0.0 if prediction == actual else 1.0

    def _save(self, result: CycleResult):
        record = asdict(result)
        self.history.append(record)

        with open(self.persistence_path, "w", encoding="utf-8") as f:
            json.dump(self.history, f, indent=2, ensure_ascii=False)

    def run_cycle(self) -> CycleResult:
        self.cycle_count += 1

        # 1. Observe current environment
        observation = self.environment.observe()

        # 2. Predict what will happen
        prediction = self.predictor.predict(observation)

        # 3. Select an action
        action = self.action_engine.select_action(
            observation,
            prediction,
        )

        # 4. Apply action to environment
        actual = self.environment.step(action)

        # 5. Compare prediction with reality
        error = self._calculate_error(prediction, actual)

        # 6. Learn from the error
        learning_applied = False

        if hasattr(self.predictor, "update"):
            self.predictor.update(
                observation=observation,
                action=action,
                prediction=prediction,
                actual=actual,
                error=error,
            )
            learning_applied = True

        # 7. Save experience to memory
        if self.memory is not None:
            if hasattr(self.memory, "store"):
                self.memory.store(
                    observation=observation,
                    prediction=prediction,
                    action=action,
                    actual=actual,
                    error=error,
                )

        # 8. Persist cycle
        result = CycleResult(
            cycle=self.cycle_count,
            observation=observation,
            prediction=prediction,
            action=action,
            actual=actual,
            error=error,
            learning_applied=learning_applied,
            timestamp=time.time(),
        )

        self._save(result)

        return result

    def run(self, cycles: int = 100):
        results = []

        for _ in range(cycles):
            result = self.run_cycle()
            results.append(result)

            print(
                f"[Cycle {result.cycle:04d}] "
                f"obs={result.observation} "
                f"pred={result.prediction} "
                f"action={result.action} "
                f"actual={result.actual} "
                f"error={result.error:.6f}"
            )

        return results
