"""
Sudha AI - Autonomous QA Loop

Version 0.1 (Educational)

Yeh loop:
1. Sawal leta hai (observation)
2. Knowledge se jawab dhoondhta hai
3. Agar actual answer diya jaye toh seekhta hai (naya fact store karta hai)
"""

from __future__ import annotations
from typing import Any, Optional
from core.answer_engine import AnswerEngine
from core.autonomous_loop import AutonomousLoop


class AutonomousQAEngine:
    """
    AnswerEngine ko autonomous loop ke saath jodta hai.
    """

    def __init__(self, answer_engine: AnswerEngine | None = None):
        self.answer_engine = answer_engine if answer_engine is not None else AnswerEngine()
        self._stopped = False
        self.history = []

    def run_cycle(self, observation: Any, actual: Any = None) -> dict:
        """
        observation = sawal (string)
        actual = sahi jawab (optional). Agar diya toh knowledge mein store ho jayega.
        """
        if self._stopped:
            return {"status": "stopped", "reason": "qa_engine_stopped"}

        if not isinstance(observation, str):
            return {
                "status": "rejected",
                "reason": "observation_must_be_string_question",
            }

        # Pehle knowledge se jawab dhoondho
        response = self.answer_engine.answer(observation)

        # Agar actual diya gaya hai aur pehle se nahi pata tha, toh seekho
        learned = False
        if actual is not None and isinstance(actual, str) and actual.strip():
            if response["status"] == "unknown":
                self.answer_engine.add_knowledge(
                    question=observation,
                    answer=actual.strip(),
                    keywords=observation.lower().split()[:5],
                )
                learned = True
                response = self.answer_engine.answer(observation)  # ab dobara try

        cycle = {
            "observation": observation,
            "prediction": response.get("answer"),
            "actual": actual,
            "status": response["status"],
            "confidence": response.get("confidence", 0.0),
            "learned": learned,
        }

        self.history.append(cycle)

        return {
            "status": "completed",
            "cycle": cycle,
            "response": response,
        }

    def is_stopped(self) -> bool:
        return self._stopped

    def stop(self):
        self._stopped = True

    def reset(self):
        self._stopped = False
        self.history.clear()
