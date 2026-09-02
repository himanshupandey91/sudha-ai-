from core.simulation import SimulationEngine


def test_simulation_uses_recent_experience():

    engine = SimulationEngine()

    result = engine.simulate(
        "use_recent_experience",
        {
            "difference": 10
        }
    )

    assert result["status"] == "completed"
    assert result["hypothesis"] == "use_recent_experience"
    assert result["predicted_difference"] == 5


def test_simulation_increases_observation():

    engine = SimulationEngine()

    result = engine.simulate(
        "increase_observation_frequency",
        {
            "difference": 10
        }
    )

    assert result["status"] == "completed"
    assert result["predicted_difference"] == 8


def test_simulation_changes_prediction_strategy():

    engine = SimulationEngine()

    result = engine.simulate(
        "change_prediction_strategy",
        {
            "difference": 10
        }
    )

    assert result["status"] == "completed"
    assert result["predicted_difference"] == 7


def test_simulation_collects_observations():

    engine = SimulationEngine()

    result = engine.simulate(
        "collect_more_observations",
        {}

    )

    assert result["status"] == "completed"
    assert result["predicted_information_gain"] == 1


def test_unknown_hypothesis_is_rejected():

    engine = SimulationEngine()

    result = engine.simulate(
        "unknown_hypothesis",
        {}
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "hypothesis_not_allowed"


def test_invalid_state_is_rejected():

    engine = SimulationEngine()

    result = engine.simulate(
        "use_recent_experience",
        "invalid"
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "state_must_be_a_dictionary"
