"""
Real Autonomous Learning Benchmark for Sudha AI

Goal:
    Test whether an agent can improve its predictions through
    repeated observe -> predict -> act -> observe -> learn cycles.

IMPORTANT:
    The environment's hidden dynamics are NOT exposed to the agent.

The benchmark measures:
    - prediction error
    - learning improvement
    - action success
    - error trend
    - statistical improvement
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean, median
from typing import List, Tuple
import math


# ============================================================
# HIDDEN ENVIRONMENT
# ============================================================

class HiddenDynamicsEnvironment:
    """
    Environment whose transition rule is hidden from the agent.

    The agent only receives:
        current_state
        available actions

    It does NOT receive:
        transition coefficient
        transition equation
        environment internals
    """

    def __init__(self, seed: float = 0.37):
        self._hidden_bias = 0.17
        self._hidden_gain = 0.73
        self._hidden_nonlinearity = 0.11

        self.state = seed
        self.steps = 0

    def reset(self, state: float = 0.37) -> float:
        self.state = state
        self.steps = 0
        return self.state

    def observe(self) -> float:
        return self.state

    def step(self, action: float) -> float:
        """
        Hidden transition dynamics.

        The agent never sees this equation.
        """

        next_state = (
            self._hidden_gain * self.state
            + 0.21 * action
            + self._hidden_bias
            + self._hidden_nonlinearity
            * math.sin(self.state * 3.0)
        )

        self.state = next_state
        self.steps += 1

        return self.state


# ============================================================
# ADAPTIVE PREDICTOR
# ============================================================

class OnlineAdaptivePredictor:
    """
    Minimal online learner.

    It learns transition dynamics from experience.

    Model:

        predicted_next =
            w_state * state
            + w_action * action
            + bias

    Parameters are updated using prediction error.

    The hidden environment equation is NOT used here.
    """

    def __init__(self, learning_rate: float = 0.03):
        self.learning_rate = learning_rate

        self.w_state = 0.0
        self.w_action = 0.0
        self.bias = 0.0

        self.samples = 0

    def predict(self, state: float, action: float) -> float:
        return (
            self.w_state * state
            + self.w_action * action
            + self.bias
        )

    def update(
        self,
        state: float,
        action: float,
        actual_next_state: float,
    ) -> Tuple[float, float]:
        prediction = self.predict(state, action)

        error = actual_next_state - prediction

        self.w_state += (
            self.learning_rate
            * error
            * state
        )

        self.w_action += (
            self.learning_rate
            * error
            * action
        )

        self.bias += self.learning_rate * error

        self.samples += 1

        return prediction, error


# ============================================================
# ACTION POLICY
# ============================================================

class SimpleExplorationPolicy:
    """
    Deterministic action policy.

    The policy intentionally explores several actions so that
    the predictor receives diverse experience.
    """

    ACTIONS = (-1.0, 0.0, 1.0)

    def select_action(self, episode: int) -> float:
        return self.ACTIONS[episode % len(self.ACTIONS)]


# ============================================================
# BENCHMARK RESULT
# ============================================================

@dataclass
class BenchmarkResult:
    errors: List[float]
    absolute_errors: List[float]
    successes: int
    episodes: int

    @property
    def initial_error(self) -> float:
        return self.absolute_errors[0]

    @property
    def final_error(self) -> float:
        return self.absolute_errors[-1]

    @property
    def mean_error(self) -> float:
        return mean(self.absolute_errors)

    @property
    def median_error(self) -> float:
        return median(self.absolute_errors)

    @property
    def improvement(self) -> float:
        if self.initial_error == 0:
            return 0.0

        return (
            self.initial_error - self.final_error
        ) / self.initial_error

    @property
    def success_rate(self) -> float:
        return self.successes / self.episodes


# ============================================================
# RUN AUTONOMOUS LOOP
# ============================================================

def run_benchmark(
    episodes: int = 300,
) -> BenchmarkResult:

    environment = HiddenDynamicsEnvironment()

    predictor = OnlineAdaptivePredictor(
        learning_rate=0.01
    )

    policy = SimpleExplorationPolicy()

    errors: List[float] = []
    absolute_errors: List[float] = []

    successes = 0

    state = environment.reset()

    for episode in range(episodes):

        # ----------------------------------------------------
        # 1. OBSERVE
        # ----------------------------------------------------

        observed_state = environment.observe()

        # ----------------------------------------------------
        # 2. ACT
        # ----------------------------------------------------

        action = policy.select_action(episode)

        # ----------------------------------------------------
        # 3. PREDICT
        # ----------------------------------------------------

        prediction = predictor.predict(
            observed_state,
            action,
        )

        # ----------------------------------------------------
        # 4. ENVIRONMENT RESPONSE
        # ----------------------------------------------------

        actual_next_state = environment.step(action)

        # ----------------------------------------------------
        # 5. PREDICTION ERROR
        # ----------------------------------------------------

        error = actual_next_state - prediction
        absolute_error = abs(error)

        errors.append(error)
        absolute_errors.append(absolute_error)

        # ----------------------------------------------------
        # 6. LEARN
        # ----------------------------------------------------

        predictor.update(
            observed_state,
            action,
            actual_next_state,
        )

        # ----------------------------------------------------
        # 7. SUCCESS METRIC
        # ----------------------------------------------------

        if absolute_error < 0.25:
            successes += 1

        state = actual_next_state

    return BenchmarkResult(
        errors=errors,
        absolute_errors=absolute_errors,
        successes=successes,
        episodes=episodes,
    )


# ============================================================
# TEST 1 — BASIC LEARNING
# ============================================================

def test_autonomous_learning_improves_prediction():

    result = run_benchmark(episodes=300)

    print("\n=== AUTONOMOUS LEARNING BENCHMARK ===")
    print(f"Episodes:        {result.episodes}")
    print(f"Initial error:   {result.initial_error:.6f}")
    print(f"Final error:     {result.final_error:.6f}")
    print(f"Mean error:      {result.mean_error:.6f}")
    print(f"Median error:    {result.median_error:.6f}")
    print(f"Improvement:     {result.improvement * 100:.2f}%")
    print(f"Success rate:    {result.success_rate * 100:.2f}%")

    assert result.final_error < result.initial_error


# ============================================================
# TEST 2 — LEARNING MUST BE SUBSTANTIAL
# ============================================================

def test_autonomous_learning_has_meaningful_improvement():

    result = run_benchmark(episodes=300)

    print(
        f"\nPrediction improvement: "
        f"{result.improvement * 100:.2f}%"
    )

    # Require at least 30% reduction from first
    # to final prediction error.
    assert result.improvement > 0.30


# ============================================================
# TEST 3 — LATE PERFORMANCE BETTER THAN EARLY PERFORMANCE
# ============================================================

def test_late_predictions_are_better_than_early_predictions():

    result = run_benchmark(episodes=300)

    early = mean(
        result.absolute_errors[:50]
    )

    late = mean(
        result.absolute_errors[-50:]
    )

    print("\n=== EARLY VS LATE ===")
    print(f"Early mean error: {early:.6f}")
    print(f"Late mean error:  {late:.6f}")

    assert late < early


# ============================================================
# TEST 4 — SUCCESS RATE IMPROVES
# ============================================================

def test_action_prediction_success_improves():

    result = run_benchmark(episodes=300)

    early_successes = sum(
        error < 0.25
        for error in result.absolute_errors[:50]
    )

    late_successes = sum(
        error < 0.25
        for error in result.absolute_errors[-50:]
    )

    print("\n=== SUCCESS RATE ===")
    print(
        f"Early: {early_successes}/50"
    )
    print(
        f"Late:  {late_successes}/50"
    )

    assert late_successes >= early_successes


# ============================================================
# TEST 5 — LEARNING TREND
# ============================================================

def test_prediction_error_trend_is_downward():

    result = run_benchmark(episodes=300)

    first_half = mean(
        result.absolute_errors[:150]
    )

    second_half = mean(
        result.absolute_errors[150:]
    )

    print("\n=== LEARNING TREND ===")
    print(f"First half:  {first_half:.6f}")
    print(f"Second half: {second_half:.6f}")

    assert second_half < first_half


if __name__ == "__main__":
    result = run_benchmark(300)

    print("\n==============================")
    print(" SUDHA AUTONOMOUS LEARNING")
    print("==============================")

    print(
        f"Initial error : {result.initial_error:.6f}"
    )

    print(
        f"Final error   : {result.final_error:.6f}"
    )

    print(
        f"Improvement   : {result.improvement * 100:.2f}%"
    )

    print(
        f"Mean error    : {result.mean_error:.6f}"
    )

    print(
        f"Success rate  : {result.success_rate * 100:.2f}%"
  )
