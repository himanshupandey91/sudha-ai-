"""
Sudha AI - Autonomous Cognitive Loop

Version 0.1

Bounded autonomous orchestration layer.

Flow:

Reason
    ↓
Hypothesis Selection
    ↓
Prediction
    ↓
Experiment
    ↓
Observed Actual
    ↓
Difference
    ↓
Learning
    ↓
Next Cycle
    ↓
Repeat until bounded limit or failure

Important:
- No invented actual outcomes.
- No uncontrolled infinite loop.
- Existing CognitiveExperimentEngine remains unchanged.
- Each cycle is executed by the real cognitive experiment engine.
- The loop only orchestrates repeated cycles.
- External observations are explicitly supplied.
"""


class AutonomousCognitiveLoop:

    def __init__(self, cognitive_engine):
        if cognitive_engine is None:
            raise ValueError(
                "cognitive_engine cannot be None"
            )

        run_cycle = getattr(
            cognitive_engine,
            "run_cycle",
            None
        )

        if not callable(run_cycle):
            raise TypeError(
                "cognitive_engine must provide run_cycle"
            )

        self.cognitive_engine = cognitive_engine

    def run(
        self,
        goal_state,
        observations,
        max_cycles=1
    ):
        """
        Execute multiple cognitive cycles automatically.

        Parameters
        ----------
        goal_state:
            Goal passed to the cognitive engine.

        observations:
            Sequence of externally supplied observations.
            One observation is consumed per cycle.

        max_cycles:
            Hard upper bound for autonomous execution.

        Returns
        -------
        dict
            Structured execution result containing
            cycle history and termination reason.
        """

        self._validate_goal(goal_state)
        self._validate_observations(observations)
        self._validate_max_cycles(max_cycles)

        if len(observations) == 0:
            return {
                "status": "unavailable",
                "reason": "no_observations",
                "cycles": [],
                "cycle_count": 0,
                "max_cycles": max_cycles
            }

        cycles = []

        cycle_limit = min(
            max_cycles,
            len(observations)
        )

        for index in range(cycle_limit):

            if self.cognitive_engine.is_stopped():
                return {
                    "status": "stopped",
                    "reason": "cognitive_engine_stopped",
                    "cycles": cycles,
                    "cycle_count": len(cycles),
                    "max_cycles": max_cycles
                }

            observation = observations[index]

            result = self.cognitive_engine.run_cycle(
                goal_state,
                observation
            )

            if not isinstance(result, dict):
                return {
                    "status": "failed",
                    "reason": "invalid_cycle_result",
                    "cycles": cycles,
                    "cycle_count": len(cycles),
                    "max_cycles": max_cycles
                }

            if result.get("status") != "completed":
                return {
                    "status": result.get(
                        "status",
                        "failed"
                    ),
                    "reason": (
                        "cycle_not_completed"
                    ),
                    "failed_cycle": index + 1,
                    "cycle_result": result,
                    "cycles": cycles,
                    "cycle_count": len(cycles),
                    "max_cycles": max_cycles
                }

            cycles.append(result)

        if len(cycles) >= max_cycles:
            reason = "max_cycles_reached"

        else:
            reason = "observations_exhausted"

        return {
            "status": "completed",
            "goal": goal_state.get("goal"),
            "cycles": cycles,
            "cycle_count": len(cycles),
            "max_cycles": max_cycles,
            "reason": reason,
            "stopped": self.cognitive_engine.is_stopped()
        }

    @staticmethod
    def _validate_goal(goal_state):
        if not isinstance(goal_state, dict):
            raise TypeError(
                "goal_state must be a dictionary"
            )

        if not goal_state.get("goal"):
            raise ValueError(
                "goal_state must contain a goal"
            )

    @staticmethod
    def _validate_observations(observations):
        if not isinstance(
            observations,
            (list, tuple)
        ):
            raise TypeError(
                "observations must be a list or tuple"
            )

    @staticmethod
    def _validate_max_cycles(max_cycles):
        if isinstance(
            max_cycles,
            bool
        ):
            raise TypeError(
                "max_cycles must be an integer"
            )

        if not isinstance(
            max_cycles,
            int
        ):
            raise TypeError(
                "max_cycles must be an integer"
            )

        if max_cycles <= 0:
            raise ValueError(
                "max_cycles must be greater than zero"
            )

    def stop(self):
        return self.cognitive_engine.stop()

    def reset(self):
        return self.cognitive_engine.reset()

    def get_history(self):
        return self.cognitive_engine.get_history()

    def get_cycle_count(self):
        return self.cognitive_engine.get_cycle_count()

    def is_stopped(self):
        return self.cognitive_engine.is_stopped()
