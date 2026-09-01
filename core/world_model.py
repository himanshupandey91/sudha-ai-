"""
Sudha AI - World Model

Version 0.1

Maintains an internal representation of the current state
based on observations and prediction results.
"""


class WorldModel:

    def __init__(self):
        self.state = {}
        self.history = []

    def update(self, observation, prediction, actual, difference):
        """
        Update the internal world state.
        """

        state = {
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": difference
        }

        self.state = state
        self.history.append(state)

        return self.state

    def get_state(self):
        """Return the current internal state."""
        return self.state

    def get_history(self):
        """Return previous states."""
        return self.history
