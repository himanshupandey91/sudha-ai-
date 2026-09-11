from core.adaptive_predictor import AdaptivePredictor
from core.predictor_persistence import PredictorPersistence


def test_learned_prediction_survives_restart(tmp_path):
    knowledge_file = (
        tmp_path / "sudha_knowledge.json"
    )

    hypothesis = (
        "effect_of_increase_temperature"
    )

    original_predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    original_predictor.set_prediction(
        hypothesis=hypothesis,
        prediction=0.0
    )

    for _ in range(100):
        original_predictor.update(
            hypothesis=hypothesis,
            actual=1.0,
        )

    learned_before_restart = (
        original_predictor.predict(hypothesis)
    )

    assert abs(
        learned_before_restart - 1.0
    ) < 0.05

    save_result = PredictorPersistence.save(
        predictor=original_predictor,
        file_path=knowledge_file,
    )

    assert save_result["status"] == "saved"

    restarted_predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    assert (
        restarted_predictor.predict(hypothesis)
        is None
    )

    load_result = PredictorPersistence.load(
        predictor=restarted_predictor,
        file_path=knowledge_file,
    )

    assert load_result["status"] == "loaded"

    learned_after_restart = (
        restarted_predictor.predict(hypothesis)
    )

    assert abs(
        learned_after_restart - 1.0
    ) < 0.05

    assert (
        learned_after_restart
        == learned_before_restart
    )
