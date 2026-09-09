"""
Sudha AI - World Model

Version 0.3

Structured world-state representation for the cognitive architecture.

Version 0.3 adds:

- Backward-compatible experience tracking
- Structured world state
- Entities and properties
- Explicit relations between entities
- Observed state transitions
- Temporal world-state history
- Deterministic state comparison
- Deep-copy isolation
- Explicit validation
- No invented reality
- No automatic causal claims
- No external side effects

Important:

The World Model records what has actually been observed or explicitly
provided by another component. It does not invent missing state,
causes, outcomes, or physical laws.
"""

from copy import deepcopy


class WorldModel:

    def __init__(self):
        """
        Initialize the world model.
        """

        # ------------------------------------------------------------------
        # Backward-compatible cognitive experience state
        # ------------------------------------------------------------------

        self.state = {
            "observation": None,
            "prediction": None,
            "actual": None,
            "difference": None,
            "learning": None,
            "experience_count": 0
        }

        self.history = []

        # ------------------------------------------------------------------
        # Structured world representation
        # ------------------------------------------------------------------

        self.world_state = {}

        self.world_history = []

        self.relations = []

        self.transition_history = []

    # ======================================================================
    # EXISTING EXPERIENCE API
    # ======================================================================

    def update(
        self,
        observation,
        prediction,
        actual,
        difference,
        learning=None
    ):
        """
        Update the cognitive experience state.

        The actual outcome must be explicitly supplied.
        The world model never invents reality.
        """

        self.state = {
            "observation": deepcopy(observation),
            "prediction": deepcopy(prediction),
            "actual": deepcopy(actual),
            "difference": deepcopy(difference),
            "learning": deepcopy(learning),
            "experience_count": len(self.history) + 1
        }

        self.history.append(
            deepcopy(self.state)
        )

        return deepcopy(self.state)

    def update_from_experience(
        self,
        experience
    ):
        """
        Update the world model from a structured experience-learning result.

        Required fields:

            observation
            prediction
            actual
            difference

        Optional:

            learning
        """

        if not isinstance(experience, dict):
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
                observation=experience["observation"],
                prediction=experience["prediction"],
                actual=experience["actual"],
                difference=experience["difference"],
                learning=experience.get("learning")
            )
        }

    def get_state(self):
        """
        Return the current cognitive experience state.
        """

        return deepcopy(self.state)

    def get_history(self):
        """
        Return previous cognitive experience states.
        """

        return deepcopy(self.history)

    def get_experience_count(self):
        """
        Return the number of recorded cognitive experiences.
        """

        return len(self.history)

    # ======================================================================
    # STRUCTURED WORLD STATE
    # ======================================================================

    def update_world_state(
        self,
        world_state
    ):
        """
        Replace the current structured world state with an explicitly
        supplied observed state.

        No state is invented by this method.
        """

        if not isinstance(world_state, dict):
            return {
                "status": "rejected",
                "reason": "world_state_must_be_a_dictionary"
            }

        self.world_state = deepcopy(world_state)

        snapshot = {
            "step": len(self.world_history) + 1,
            "state": deepcopy(self.world_state)
        }

        self.world_history.append(
            snapshot
        )

        return {
            "status": "updated",
            "world_state": deepcopy(self.world_state),
            "step": snapshot["step"]
        }

    def get_world_state(self):
        """
        Return the current structured world state.
        """

        return deepcopy(self.world_state)

    def get_world_history(self):
        """
        Return temporal world-state history.
        """

        return deepcopy(self.world_history)

    # ======================================================================
    # ENTITIES
    # ======================================================================

    def add_entity(
        self,
        entity_id,
        properties=None
    ):
        """
        Add a new entity to the world state.

        Example:

            add_entity(
                "machine",
                {
                    "power": "off",
                    "temperature": 20
                }
            )
        """

        if not isinstance(entity_id, str) or not entity_id.strip():
            return {
                "status": "rejected",
                "reason": "entity_id_must_be_a_non_empty_string"
            }

        if properties is None:
            properties = {}

        if not isinstance(properties, dict):
            return {
                "status": "rejected",
                "reason": "entity_properties_must_be_a_dictionary"
            }

        if entity_id in self.world_state:
            return {
                "status": "rejected",
                "reason": "entity_already_exists",
                "entity_id": entity_id
            }

        self.world_state[entity_id] = deepcopy(properties)

        self._record_world_snapshot()

        return {
            "status": "added",
            "entity_id": entity_id,
            "entity": deepcopy(
                self.world_state[entity_id]
            )
        }

    def update_entity(
        self,
        entity_id,
        properties
    ):
        """
        Update properties of an existing entity.

        An unknown entity is rejected instead of silently invented.
        """

        if not isinstance(entity_id, str) or not entity_id.strip():
            return {
                "status": "rejected",
                "reason": "entity_id_must_be_a_non_empty_string"
            }

        if not isinstance(properties, dict):
            return {
                "status": "rejected",
                "reason": "entity_properties_must_be_a_dictionary"
            }

        if entity_id not in self.world_state:
            return {
                "status": "rejected",
                "reason": "entity_not_found",
                "entity_id": entity_id
            }

        current_properties = self.world_state[entity_id]

        if not isinstance(current_properties, dict):
            return {
                "status": "rejected",
                "reason": "existing_entity_state_must_be_a_dictionary",
                "entity_id": entity_id
            }

        current_properties.update(
            deepcopy(properties)
        )

        self._record_world_snapshot()

        return {
            "status": "updated",
            "entity_id": entity_id,
            "entity": deepcopy(
                self.world_state[entity_id]
            )
        }

    def get_entity(
        self,
        entity_id
    ):
        """
        Return an entity by ID.

        Returns None when the entity does not exist.
        """

        if entity_id not in self.world_state:
            return None

        return deepcopy(
            self.world_state[entity_id]
        )

    # ======================================================================
    # RELATIONS
    # ======================================================================

    def add_relation(
        self,
        subject,
        relation,
        object
    ):
        """
        Add an explicit relation between two entities.

        Example:

            machine --located_in--> lab

        This method records the relation exactly as supplied.
        It does not infer additional relationships.
        """

        values = {
            "subject": subject,
            "relation": relation,
            "object": object
        }

        for field, value in values.items():

            if not isinstance(value, str) or not value.strip():

                return {
                    "status": "rejected",
                    "reason": f"{field}_must_be_a_non_empty_string"
                }

        relation_record = {
            "subject": subject,
            "relation": relation,
            "object": object
        }

        if relation_record in self.relations:

            return {
                "status": "rejected",
                "reason": "relation_already_exists",
                "relation": deepcopy(relation_record)
            }

        self.relations.append(
            deepcopy(relation_record)
        )

        return {
            "status": "added",
            "relation": deepcopy(relation_record)
        }

    def get_relations(self):
        """
        Return all explicit relations.
        """

        return deepcopy(self.relations)

    # ======================================================================
    # OBSERVED TRANSITIONS
    # ======================================================================

    def record_transition(
        self,
        action,
        before_state,
        after_state
    ):
        """
        Record an observed state transition.

        Both before_state and after_state must be explicitly supplied.

        The method reports what changed, but does not claim why it changed.

        Example:

            before:
                {"machine": {"power": "off"}}

            action:
                {"type": "switch_on"}

            after:
                {"machine": {"power": "on"}}
        """

        if not isinstance(action, dict):
            return {
                "status": "rejected",
                "reason": "action_must_be_a_dictionary"
            }

        if not isinstance(before_state, dict):
            return {
                "status": "rejected",
                "reason": "before_state_must_be_a_dictionary"
            }

        if not isinstance(after_state, dict):
            return {
                "status": "rejected",
                "reason": "after_state_must_be_a_dictionary"
            }

        changed = self._compute_state_changes(
            before_state,
            after_state
        )

        transition = {
            "step": len(self.transition_history) + 1,
            "action": deepcopy(action),
            "before": deepcopy(before_state),
            "after": deepcopy(after_state),
            "changed": deepcopy(changed)
        }

        self.transition_history.append(
            transition
        )

        # The after-state is explicitly observed, so it becomes
        # the current world state.
        self.world_state = deepcopy(after_state)

        self._record_world_snapshot()

        return {
            "status": "recorded",
            "transition": deepcopy(transition)
        }

    def get_transition_history(self):
        """
        Return all recorded observed transitions.
        """

        return deepcopy(
            self.transition_history
        )

    # ======================================================================
    # STATE COMPARISON
    # ======================================================================

    def compare_states(
        self,
        before_state,
        after_state
    ):
        """
        Compare two explicitly supplied world states.

        Returns only observed structural differences.
        It does not infer causality.
        """

        if not isinstance(before_state, dict):
            return {
                "status": "rejected",
                "reason": "before_state_must_be_a_dictionary"
            }

        if not isinstance(after_state, dict):
            return {
                "status": "rejected",
                "reason": "after_state_must_be_a_dictionary"
            }

        return {
            "status": "compared",
            "changed": self._compute_state_changes(
                before_state,
                after_state
            )
        }

    # ======================================================================
    # INTERNAL HELPERS
    # ======================================================================

    def _record_world_snapshot(self):
        """
        Record a deep copy of the current world state.
        """

        self.world_history.append(
            {
                "step": len(self.world_history) + 1,
                "state": deepcopy(self.world_state)
            }
        )

    @staticmethod
    def _compute_state_changes(
        before_state,
        after_state
    ):
        """
        Compute deterministic top-level state differences.

        Missing keys are explicitly represented so that a real value of
        None is not confused with a missing key.
        """

        changes = {}

        all_keys = set(
            before_state.keys()
        ) | set(
            after_state.keys()
        )

        for key in sorted(
            all_keys,
            key=lambda value: repr(value)
        ):

            before_present = key in before_state
            after_present = key in after_state

            before_value = (
                before_state[key]
                if before_present
                else None
            )

            after_value = (
                after_state[key]
                if after_present
                else None
            )

            if (
                before_present != after_present
                or before_value != after_value
            ):

                changes[key] = {
                    "before_present": before_present,
                    "before": deepcopy(
                        before_value
                    ),
                    "after_present": after_present,
                    "after": deepcopy(
                        after_value
                    )
                }

        return changes

    # ======================================================================
    # RESET
    # ======================================================================

    def clear(self):
        """
        Clear all world-model state and history.
        """

        self.history.clear()

        self.world_history.clear()

        self.relations.clear()

        self.transition_history.clear()

        self.state = {
            "observation": None,
            "prediction": None,
            "actual": None,
            "difference": None,
            "learning": None,
            "experience_count": 0
        }

        self.world_state = {}

        return {
            "status": "cleared"
            }
