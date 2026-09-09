from core.world_model import WorldModel


def test_world_model_update():

    model = WorldModel()

    state = model.update(
        observation=10,
        prediction=10,
        actual=15,
        difference=5
    )

    assert state["observation"] == 10
    assert state["prediction"] == 10
    assert state["actual"] == 15
    assert state["difference"] == 5

    assert len(model.get_history()) == 1


def test_world_model_add_object():

    model = WorldModel()

    result = model.add_object(
        "cup",
        {
            "color": "red",
            "location": "table"
        }
    )

    assert result["status"] == "object_added"

    cup = model.get_object("cup")

    assert cup["properties"]["color"] == "red"
    assert cup["properties"]["location"] == "table"


def test_world_model_updates_existing_object():

    model = WorldModel()

    model.add_object(
        "cup",
        {"location": "table"}
    )

    model.update_object(
        "cup",
        {"color": "blue"}
    )

    cup = model.get_object("cup")

    assert cup["properties"]["location"] == "table"
    assert cup["properties"]["color"] == "blue"


def test_world_model_relation():

    model = WorldModel()

    model.add_object("cup")
    model.add_object("table")

    result = model.add_relation(
        "cup",
        "ON",
        "table"
    )

    assert result["status"] == "relation_added"

    relations = model.get_relations()

    assert relations == [
        {
            "subject": "cup",
            "relation": "ON",
            "object": "table"
        }
    ]


def test_world_model_remove_relation():

    model = WorldModel()

    model.add_object("cup")
    model.add_object("table")

    model.add_relation(
        "cup",
        "ON",
        "table"
    )

    result = model.remove_relation(
        "cup",
        "ON",
        "table"
    )

    assert result["status"] == "relation_removed"
    assert model.get_relations() == []


def test_world_model_action_changes_state():

    model = WorldModel()

    model.add_object(
        "cup",
        {"location": "table"}
    )

    result = model.apply_action(
        "move",
        "cup",
        {"location": "hand"}
    )

    assert result["status"] == "transition_applied"

    cup = model.get_object("cup")

    assert cup["properties"]["location"] == "hand"


def test_world_model_prediction_does_not_change_state():

    model = WorldModel()

    model.add_object(
        "cup",
        {"location": "table"}
    )

    prediction = model.predict_next_state(
        "move",
        "cup",
        {"location": "hand"}
    )

    assert prediction["status"] == "prediction_created"

    assert (
        prediction["predicted_object"]["properties"][
            "location"
        ]
        == "hand"
    )

    cup = model.get_object("cup")

    assert cup["properties"]["location"] == "table"


def test_world_model_rejects_unknown_object():

    model = WorldModel()

    result = model.apply_action(
        "move",
        "cup",
        {"location": "hand"}
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "object_not_found"


def test_world_model_rejects_unknown_action():

    model = WorldModel()

    model.add_object("cup")

    result = model.apply_action(
        "fly",
        "cup",
        {}
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "unsupported_action"


def test_world_model_clear():

    model = WorldModel()

    model.add_object(
        "cup",
        {"location": "table"}
    )

    model.update(
        observation=1,
        prediction=2,
        actual=3,
        difference=1
    )

    result = model.clear()

    assert result["status"] == "cleared"
    assert model.get_experience_count() == 0
    assert model.get_state()["objects"] == {}
    assert model.get_state()["relations"] == []
