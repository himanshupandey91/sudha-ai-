"""
Sudha AI - Predictor Persistence

Saves and loads learned predictions so that knowledge
can survive a process restart.
"""

from __future__ import annotations

import json
from pathlib import Path


class PredictorPersistence:
    @staticmethod
    def save(predictor, file_path):
        if predictor is None:
            raise ValueError("predictor must not be None")

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "predictions": predictor.predictions,
            "history": predictor.history,
            "configuration": predictor.get_configuration(),
        }

        with path.open("w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=2,
                sort_keys=True,
            )

        return {
            "status": "saved",
            "file_path": str(path),
        }

    @staticmethod
    def load(predictor, file_path):
        if predictor is None:
            raise ValueError("predictor must not be None")

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"knowledge file not found: {path}"
            )

        with path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                "knowledge file must contain a dictionary"
            )

        predictions = data.get("predictions", {})
        history = data.get("history", {})

        if not isinstance(predictions, dict):
            raise ValueError(
                "predictions must be a dictionary"
            )

        if not isinstance(history, dict):
            raise ValueError(
                "history must be a dictionary"
            )

        predictor.predictions = predictions
        predictor.history = history

        return {
            "status": "loaded",
            "file_path": str(path),
            "predictions": dict(predictor.predictions),
        }
