from core.world_model import WorldModel


def test_world_model_update():
    world_model = WorldModel()

    result = world_model.update(
        observation=10,
        prediction=10,
        actual=15,
        difference=5
    )

    assert result["observation"] == 10
    assert result["prediction"] == 10
    assert result["actual"] == 15
    assert result["difference"] == 5
    assert result["experience_count"] == 1

    assert world_model.get_experience_count() == 1


def test_world_model_preserves_experience_history():
    world_model = WorldModel()

    world_model.update(
        observation=10,
        prediction=12,
        actual=15,
        difference=3
    )

    world_model.update(
        observation=20,
        prediction=18,
        actual=17,
        difference=1
    )

    history = world_model.get_history()

    assert len(history) == 2
    assert history[0]["observation"] == 10
    assert history[1]["observation"] == 20


def test_world_model_update_from_experience():
    world_model = WorldModel()

    result = world_model.update_from_experience(
        {
            "observation": 10,
            "prediction": 12,
            "actual": 15,
            "difference": 3,
            "learning": {
                "status": "learned"
            }
        }
    )

    assert result["status"] == "updated"
    assert result["state"]["actual"] == 15
    assert result["state"]["learning"]["status"] == "learned"


def test_world_model_rejects_invalid_experience():
    world_model = WorldModel()

    result = world_model.update_from_experience(
        "invalid"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "experience_must_be_a_dictionary"


def test_world_model_rejects_missing_experience_field():
    world_model = WorldModel()

    result = world_model.update_from_experience(
        {
            "observation": 10,
            "prediction": 12,
            "actual": 15
        }
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "experience_field_missing"
    assert result["field"] == "difference"


def test_world_model_update_world_state():
    world_model = WorldModel()

    result = world_model.update_world_state(
        {
            "machine": {
                "power": "off",
                "temperature": 20
            }
        }
    )

    assert result["status"] == "updated"

    assert world_model.get_world_state() == {
        "machine": {
            "power": "off",
            "temperature": 20
        }
    }

    assert result["step"] == 1


def test_world_model_rejects_invalid_world_state():
    world_model = WorldModel()

    result = world_model.update_world_state(
        ["invalid"]
    )

    assert result["status"] == "rejected"
    assert result["reason"] == (
        "world_state_must_be_a_dictionary"
    )


def test_world_model_add_entity():
    world_model = WorldModel()

    result = world_model.add_entity(
        "machine",
        {
            "power": "off",
            "temperature": 20
        }
    )

    assert result["status"] == "added"
    assert result["entity_id"] == "machine"

    assert world_model.get_entity("machine") == {
        "power": "off",
        "temperature": 20
    }


def test_world_model_rejects_duplicate_entity():
    world_model = WorldModel()

    world_model.add_entity(
        "machine",
        {
            "power": "off"
        }
    )

    result = world_model.add_entity(
        "machine",
        {
            "power": "on"
        }
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "entity_already_exists"


def test_world_model_updates_existing_entity():
    world_model = WorldModel()

    world_model.add_entity(
        "machine",
        {
            "power": "off",
            "temperature": 20
        }
    )

    result = world_model.update_entity(
        "machine",
        {
            "power": "on"
        }
    )

    assert result["status"] == "updated"

    assert world_model.get_entity("machine") == {
        "power": "on",
        "temperature": 20
    }


def test_world_model_rejects_unknown_entity_update():
    world_model = WorldModel()

    result = world_model.update_entity(
        "unknown",
        {
            "power": "on"
        }
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "entity_not_found"


def test_world_model_adds_explicit_relation():
    world_model = WorldModel()

    result = world_model.add_relation(
        "machine",
        "located_in",
        "lab"
    )

    assert result["status"] == "added"

    assert world_model.get_relations() == [
        {
            "subject": "machine",
            "relation": "located_in",
            "object": "lab"
        }
    ]


def test_world_model_rejects_duplicate_relation():
    world_model = WorldModel()

    world_model.add_relation(
        "machine",
        "located_in",
        "lab"
    )

    result = world_model.add_relation(
        "machine",
        "located_in",
        "lab"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "relation_already_exists"


def test_world_model_records_observed_transition():
    world_model = WorldModel()

    before = {
        "machine": {
            "power": "off",
            "temperature": 20
        }
    }

    after = {
        "machine": {
            "power": "on",
            "temperature": 25
        }
    }

    result = world_model.record_transition(
        action={
            "type": "switch_on"
        },
        before_state=before,
        after_state=after
    )

    assert result["status"] == "recorded"

    transition = result["transition"]

    assert transition["step"] == 1
    assert transition["action"]["type"] == "switch_on"
    assert transition["before"] == before
    assert transition["after"] == after

    assert "machine" in transition["changed"]


def test_world_model_transition_updates_current_state():
    world_model = WorldModel()

    before = {
        "machine": {
            "power": "off"
        }
    }

    after = {
        "machine": {
            "power": "on"
        }
    }

    world_model.record_transition(
        action={
            "type": "switch_on"
        },
        before_state=before,
        after_state=after
    )

    assert world_model.get_world_state() == after


def test_world_model_compare_states():
    world_model = WorldModel()

    before = {
        "temperature": 20,
        "power": "off"
    }

    after = {
        "temperature": 25,
        "power": "on"
    }

    result = world_model.compare_states(
        before,
        after
    )

    assert result["status"] == "compared"

    changes = result["changed"]

    assert changes["temperature"]["before"] == 20
    assert changes["temperature"]["after"] == 25

    assert changes["power"]["before"] == "off"
    assert changes["power"]["after"] == "on"


def test_world_model_does_not_invent_missing_state():
    world_model = WorldModel()

    result = world_model.update_entity(
        "machine",
        {
            "power": "on"
        }
    )

    assert result["status"] == "rejected"

    assert world_model.get_world_state() == {}


def test_world_model_deep_copy_isolation():
    world_model = WorldModel()

    source = {
        "machine": {
            "temperature": 20
        }
    }

    world_model.update_world_state(
        source
    )

    source["machine"]["temperature"] = 999

    assert (
        world_model.get_world_state()[
            "machine"
        ]["temperature"]
        == 20
    )


def test_world_model_history_is_deep_copy():
    world_model = WorldModel()

    world_model.update_world_state(
        {
            "machine": {
                "temperature": 20
            }
        }
    )

    history = world_model.get_world_history()

    history[0]["state"]["machine"]["temperature"] = 999

    assert (
        world_model.get_world_history()[
            0
        ]["state"]["machine"]["temperature"]
        == 20
    )


def test_world_model_clear_resets_everything():
    world_model = WorldModel()

    world_model.update(
        observation=10,
        prediction=12,
        actual=15,
        difference=3
    )

    world_model.update_world_state(
        {
            "machine": {
                "power": "on"
            }
        }
    )

    world_model.add_relation(
        "machine",
        "located_in",
        "lab"
    )

    world_model.record_transition(
        action={
            "type": "observe"
        },
        before_state={
            "machine": {
                "power": "off"
            }
        },
        after_state={
            "machine": {
                "power": "on"
            }
        }
    )

    result = world_model.clear()

    assert result["status"] == "cleared"

    assert world_model.get_state() == {
        "observation": None,
        "prediction": None,
        "actual": None,
        "difference": None,
        "learning": None,
        "experience_count": 0
    }

    assert world_model.get_history() == []
    assert world_model.get_world_state() == {}
    assert world_model.get_world_history() == []
    assert world_model.get_relations() == []
    assert world_model.get_transition_history() == []
