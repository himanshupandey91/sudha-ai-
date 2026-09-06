"""
Sudha AI - World Model

Version 0.2

Maintains an internal representation of the
current state of the environment and learning cycle.

Version 0.2:
- Stores observation
- Stores prediction
- Stores actual outcome
- Stores prediction difference
- Stores learning information
- Tracks experience count
- Provides structured current state
- Preserves historical states
- Deterministic behavior
- No external side effects
"""


class WorldModel:

    def __init__(self):
        """
        Initialize the world model.
        """

        self.state = {
            "observation": None,
            "prediction": None,
            "actual": None,
            "difference": None,
            "learning": None,
            "experience_count": 0
        }

        self.history = []

    def update(
        self,
        observation,
        prediction,
        actual,
        difference,
        learning=None
    ):
        """
        Update the internal world state.

        The actual outcome must be explicitly supplied.
        The world model never invents reality.
        """

        self.state = {
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": difference,
            "learning": learning,
            "experience_count": (
                len(self.history) + 1
            )
        }

        self.history.append(
            dict(self.state)
        )

        return dict(self.state)

    def update_from_experience(
        self,
        experience
    ):
        """
        Update the world model from a structured
        experience-learning result.

        Expected fields:

            observation
            prediction
            actual
            difference

        Optional:

            learning
        """

        if not isinstance(
            experience,
            dict
        ):
            return {
                "status": "rejected",
                "reason": "experience_must_be_a_dictionary"
            }

        required_fields = (
            "observation",
            "prediction",
            "actual",
            "difference"
        )

        for field in required_fields:

            if field not in experience:

                return {
                    "status": "rejected",
                    "reason": (
                        "experience_field_missing"
                    ),
                    "field": field
                }

        return {
            "status": "updated",
            "state": self.update(
                observation=experience[
                    "observation"
                ],
                prediction=experience[
                    "prediction"
                ],
                actual=experience[
                    "actual"
                ],
                difference=experience[
                    "difference"
                ],
                learning=experience.get(
                    "learning"
                )
            )
        }

    def get_state(self):
        """
        Return the current internal state.
        """

        return dict(
            self.state
        )

    def get_history(self):
        """
        Return previous world states.
        """

        return [
            dict(state)
            for state in self.history
        ]

    def get_experience_count(self):
        """
        Return the number of recorded experiences.
        """

        return len(
            self.history
        )

    def clear(self):
        """
        Clear the world model history and
        reset the current state.
        """

        self.history.clear()

        self.state = {
            "observation": None,
            "prediction": None,
            "actual": None,
            "difference": None,
            "learning": None,
            "experience_count": 0
        }

        return {
            "status": "cleared"
        }
