from core.adaptive_predictor import AdaptivePredictor
from core.environment import Environment


def test_prediction_error_decreases_over_repeated_cycles():
    environment = Environment()

    predictor = AdaptivePredictor(
        learning_rate=0.5
    )

    hypothesis = "predict_temperature"

    predictor.set_prediction(
        hypothesis=hypothesis,
        prediction=0.0
    )

    errors = []

    for _ in range(10):
        result = environment.step("observe")

        actual = result["actual"]

        prediction = predictor.predict(hypothesis)

        error = abs(actual - prediction)

        errors.append(error)

        predictor.update(
            hypothesis=hypothesis,
            actual=actual
        )

    assert errors[0] > errors[-1]

    assert errors[-1] < 0.05

    assert all(
        errors[index + 1] < errors[index]
        for index in range(len(errors) - 1)
    )
