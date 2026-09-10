from core.environment import Environment, EnvironmentError


def test_environment_starts_with_initial_state():
    environment = Environment(
        initial_state={
            "temperature": 20.0,
            "machine": "OFF",
        }
    )

    assert environment.get_state() == {
        "temperature": 20.0,
        "machine": "OFF",
    }


def test_increase_temperature_changes_real_environment_state():
    environment = Environment(
        initial_state={
            "temperature": 20.0,
            "machine": "OFF",
        }
    )

    result = environment.step("increase_temperature")

    assert result["status"] == "completed"
    assert result["action"] == "increase_temperature"

    assert result["before_state"]["temperature"] == 20.0
    assert result["after_state"]["temperature"] == 21.0

    assert result["actual"] == 21.0


def test_decrease_temperature_changes_real_environment_state():
    environment = Environment(
        initial_state={
            "temperature": 20.0,
            "machine": "OFF",
        }
    )

    result = environment.step("decrease_temperature")

    assert result["before_state"]["temperature"] == 20.0
    assert result["after_state"]["temperature"] == 19.0

    assert result["actual"] == 19.0


def test_switch_on_changes_machine_state():
    environment = Environment(
        initial_state={
            "temperature": 20.0,
            "machine": "OFF",
        }
    )

    result = environment.step("switch_on")

    assert result["before_state"]["machine"] == "OFF"
    assert result["after_state"]["machine"] == "ON"


def test_switch_off_changes_machine_state():
    environment = Environment(
        initial_state={
            "temperature": 20.0,
            "machine": "ON",
        }
    )

    result = environment.step("switch_off")

    assert result["before_state"]["machine"] == "ON"
    assert result["after_state"]["machine"] == "OFF"


def test_observe_does_not_change_environment_state():
    environment = Environment(
        initial_state={
            "temperature": 20.0,
            "machine": "OFF",
        }
    )

    before = environment.get_state()

    result = environment.step("observe")

    after = environment.get_state()

    assert result["status"] == "completed"
    assert before == after
    assert result["actual"] == 20.0


def test_reset_restores_initial_state():
    environment = Environment(
        initial_state={
            "temperature": 20.0,
            "machine": "OFF",
        }
    )

    environment.step("increase_temperature")
    environment.step("switch_on")

    assert environment.get_state() == {
        "temperature": 21.0,
        "machine": "ON",
    }

    state = environment.reset()

    assert state == {
        "temperature": 20.0,
        "machine": "OFF",
    }

    assert environment.get_state() == {
        "temperature": 20.0,
        "machine": "OFF",
    }


def test_environment_returns_copies_of_state():
    environment = Environment(
        initial_state={
            "temperature": 20.0,
            "machine": "OFF",
        }
    )

    state = environment.get_state()
    state["temperature"] = 999.0

    assert environment.get_state()["temperature"] == 20.0


def test_environment_rejects_unknown_action():
    environment = Environment()

    try:
        environment.step("unknown_action")
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_environment_rejects_non_string_action():
    environment = Environment()

    try:
        environment.step(123)
        assert False, "Expected TypeError"
    except TypeError:
        pass


def test_environment_rejects_non_numeric_temperature_for_temperature_action():
    environment = Environment(
        initial_state={
            "temperature": "unknown",
            "machine": "OFF",
        }
    )

    try:
        environment.step("increase_temperature")
        assert False, "Expected EnvironmentError"
    except EnvironmentError:
        pass


def test_environment_produces_actual_from_state_after_transition():
    environment = Environment(
        initial_state={
            "temperature": 20.0,
            "machine": "OFF",
        }
    )

    first = environment.step("increase_temperature")
    second = environment.step("increase_temperature")

    assert first["actual"] == 21.0
    assert second["actual"] == 22.0

    assert environment.get_state()["temperature"] == 22.0
