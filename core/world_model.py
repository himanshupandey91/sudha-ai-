"""
Sudha AI - Stateful World Model

Version 1.0

Maintains:
- Current environment state
- Objects and their properties
- Relations between objects
- Action-driven state transitions
- Observations
- Predictions
- Actual outcomes
- Prediction errors
- Learning information
- Historical world states
- Experience count

Design principles:
- Deterministic
- Explicit state transitions
- No invented observations
- No external side effects
- Backward compatible with Version 0.2 update()
"""


class WorldModel:

    def __init__(self):
        """Initialize the world model."""

        self.state = self._empty_state()
        self.history = []

    # ------------------------------------------------------------------
    # STATE
    # ------------------------------------------------------------------

    @staticmethod
    def _empty_state():
        return {
            "observation": None,
            "prediction": None,
            "actual": None,
            "difference": None,
            "learning": None,
            "experience_count": 0,

            # Stateful world representation
            "objects": {},
            "relations": [],
            "last_action": None,
            "transition_count": 0
        }

    def get_state(self):
        """Return a copy of the current world state."""

        return {
            **self.state,
            "objects": {
                name: dict(properties)
                for name, properties in self.state["objects"].items()
            },
            "relations": [
                dict(relation)
                for relation in self.state["relations"]
            ]
        }

    # ------------------------------------------------------------------
    # OBJECTS
    # ------------------------------------------------------------------

    def add_object(
        self,
        object_id,
        properties=None
    ):
        """
        Add an object to the world.

        Existing objects are updated rather than duplicated.
        """

        if not isinstance(object_id, str):
            raise TypeError(
                "object_id must be a string"
            )

        if not object_id:
            raise ValueError(
                "object_id must not be empty"
            )

        if properties is None:
            properties = {}

        if not isinstance(properties, dict):
            raise TypeError(
                "properties must be a dictionary"
            )

        existing = self.state["objects"].get(
            object_id,
            {}
        )

        existing.update(properties)

        self.state["objects"][object_id] = existing

        return {
            "status": "object_added",
            "object_id": object_id,
            "properties": dict(existing)
        }

    def update_object(
        self,
        object_id,
        properties
    ):
        """Update properties of an existing object."""

        if object_id not in self.state["objects"]:
            return {
                "status": "rejected",
                "reason": "object_not_found",
                "object_id": object_id
            }

        if not isinstance(properties, dict):
            raise TypeError(
                "properties must be a dictionary"
            )

        self.state["objects"][object_id].update(
            properties
        )

        return {
            "status": "object_updated",
            "object_id": object_id,
            "properties": dict(
                self.state["objects"][object_id]
            )
        }

    def get_object(self, object_id):
        """Return an object state."""

        if object_id not in self.state["objects"]:
            return None

        return {
            "object_id": object_id,
            "properties": dict(
                self.state["objects"][object_id]
            )
        }

    # ------------------------------------------------------------------
    # RELATIONS
    # ------------------------------------------------------------------

    def add_relation(
        self,
        subject,
        relation,
        object_id
    ):
        """
        Add an explicit relation.

        Example:

            cup ON table
        """

        if subject not in self.state["objects"]:
            return {
                "status": "rejected",
                "reason": "subject_not_found",
                "subject": subject
            }

        if object_id not in self.state["objects"]:
            return {
                "status": "rejected",
                "reason": "object_not_found",
                "object": object_id
            }

        if not isinstance(relation, str):
            raise TypeError(
                "relation must be a string"
            )

        relation_record = {
            "subject": subject,
            "relation": relation,
            "object": object_id
        }

        if relation_record not in self.state["relations"]:
            self.state["relations"].append(
                relation_record
            )

        return {
            "status": "relation_added",
            "relation": dict(relation_record)
        }

    def remove_relation(
        self,
        subject,
        relation,
        object_id
    ):
        """Remove an explicit relation."""

        target = {
            "subject": subject,
            "relation": relation,
            "object": object_id
        }

        before = len(
            self.state["relations"]
        )

        self.state["relations"] = [
            item
            for item in self.state["relations"]
            if item != target
        ]

        if len(self.state["relations"]) == before:
            return {
                "status": "not_found"
            }

        return {
            "status": "relation_removed",
            "relation": target
        }

    def get_relations(self):
        """Return all known relations."""

        return [
            dict(relation)
            for relation in self.state["relations"]
        ]

    # ------------------------------------------------------------------
    # ACTION / STATE TRANSITION
    # ------------------------------------------------------------------

    def apply_action(
        self,
        action,
        object_id,
        properties=None
    ):
        """
        Apply an explicit state transition.

        Supported actions:

            set_property
            move
            delete_property

        The world model does not invent the action result.
        The requested transition is applied deterministically.
        """

        if object_id not in self.state["objects"]:
            return {
                "status": "rejected",
                "reason": "object_not_found",
                "object_id": object_id
            }

        if properties is None:
            properties = {}

        if not isinstance(properties, dict):
            raise TypeError(
                "properties must be a dictionary"
            )

        if action == "set_property":

            self.state["objects"][object_id].update(
                properties
            )

        elif action == "move":

            if "location" not in properties:
                return {
                    "status": "rejected",
                    "reason": "location_required"
                }

            self.state["objects"][object_id][
                "location"
            ] = properties["location"]

        elif action == "delete_property":

            for key in properties:
                self.state["objects"][object_id].pop(
                    key,
                    None
                )

        else:

            return {
                "status": "rejected",
                "reason": "unsupported_action",
                "action": action
            }

        self.state["last_action"] = {
            "action": action,
            "object_id": object_id,
            "properties": dict(properties)
        }

        self.state["transition_count"] += 1

        return {
            "status": "transition_applied",
            "action": action,
            "object_id": object_id,
            "state": self.get_object(object_id)
        }

    # ------------------------------------------------------------------
    # FUTURE STATE PREDICTION
    # ------------------------------------------------------------------

    def predict_next_state(
        self,
        action,
        object_id,
        properties=None
    ):
        """
        Predict the next state without modifying the world.

        This is a model-based transition prediction.

        It does NOT claim that the predicted state actually happened.
        """

        if object_id not in self.state["objects"]:
            return {
                "status": "rejected",
                "reason": "object_not_found"
            }

        if properties is None:
            properties = {}

        if not isinstance(properties, dict):
            raise TypeError(
                "properties must be a dictionary"
            )

        predicted_properties = dict(
            self.state["objects"][object_id]
        )

        if action in (
            "set_property",
            "move"
        ):

            predicted_properties.update(
                properties
            )

        elif action == "delete_property":

            for key in properties:
                predicted_properties.pop(
                    key,
                    None
                )

        else:

            return {
                "status": "rejected",
                "reason": "unsupported_action",
                "action": action
            }

        return {
            "status": "prediction_created",
            "action": action,
            "object_id": object_id,
            "predicted_object": {
                "object_id": object_id,
                "properties": predicted_properties
            }
        }

    # ------------------------------------------------------------------
    # EXPERIENCE / LEARNING
    # ------------------------------------------------------------------

    def update(
        self,
        observation,
        prediction,
        actual,
        difference,
        learning=None
    ):
        """
        Record an experience.

        This preserves the Version 0.2 API.
        """

        self.state = {
            **self.state,
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": difference,
            "learning": learning,
            "experience_count": len(
                self.history
            ) + 1
        }

        self.history.append(
            self.get_state()
        )

        return self.get_state()

    def update_from_experience(
        self,
        experience
    ):
        """
        Update the world model from a structured
        experience-learning result.
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
                    "reason": "experience_field_missing",
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

    # ------------------------------------------------------------------
    # HISTORY
    # ------------------------------------------------------------------

    def get_history(self):
        """Return previous world states."""

        return [
            {
                **state,
                "objects": {
                    name: dict(properties)
                    for name, properties
                    in state["objects"].items()
                },
                "relations": [
                    dict(relation)
                    for relation in state["relations"]
                ]
            }
            for state in self.history
        ]

    def get_experience_count(self):
        """Return number of recorded experiences."""

        return len(
            self.history
        )

    # ------------------------------------------------------------------
    # RESET
    # ------------------------------------------------------------------

    def clear(self):
        """Reset the complete world model."""

        self.history.clear()

        self.state = self._empty_state()

        return {
            "status": "cleared"
        }
