"""
Sudha AI - Simple Knowledge Base

Version 0.1 (Educational)

Yeh ek bahut simple knowledge store hai.
- Text / keyword based retrieval
- Koi embedding, vector DB, ya LLM nahi hai
- Sirf stored facts se answer nikalta hai

Limitation:
- Sirf wahi jawab de sakta hai jo knowledge mein pehle se pada ho
- Real understanding nahi hai
"""

from __future__ import annotations
from typing import Any


class KnowledgeBase:
    """
    Simple in-memory knowledge base.
    """

    def __init__(self):
        self._facts: list[dict] = []

    def add_fact(self, question: str, answer: str, keywords: list[str] | None = None) -> dict:
        """
        Ek naya fact store karo.
        """
        if not isinstance(question, str) or not question.strip():
            return {"status": "rejected", "reason": "question_must_be_non_empty_string"}

        if not isinstance(answer, str) or not answer.strip():
            return {"status": "rejected", "reason": "answer_must_be_non_empty_string"}

        fact = {
            "question": question.strip().lower(),
            "answer": answer.strip(),
            "keywords": [k.lower().strip() for k in (keywords or []) if k.strip()],
        }

        self._facts.append(fact)

        return {
            "status": "stored",
            "count": len(self._facts),
        }

    def search(self, query: str) -> dict:
        """
        Query se related fact dhoondho.
        Simple keyword + substring matching.
        """
        if not isinstance(query, str) or not query.strip():
            return {
                "status": "rejected",
                "reason": "query_must_be_non_empty_string",
            }

        query_lower = query.strip().lower()
        query_words = set(query_lower.split())

        best_score = 0
        best_fact = None

        for fact in self._facts:
            score = 0

            # Exact question match
            if query_lower == fact["question"]:
                score += 100

            # Substring match
            if query_lower in fact["question"] or fact["question"] in query_lower:
                score += 40

            # Keyword match
            for kw in fact["keywords"]:
                if kw in query_lower:
                    score += 15

            # Word overlap
            fact_words = set(fact["question"].split())
            overlap = len(query_words & fact_words)
            score += overlap * 10

            if score > best_score:
                best_score = score
                best_fact = fact

        if best_fact is None or best_score < 10:
            return {
                "status": "not_found",
                "query": query,
                "score": best_score,
            }

        return {
            "status": "found",
            "query": query,
            "matched_question": best_fact["question"],
            "answer": best_fact["answer"],
            "score": best_score,
        }

    def get_all_facts(self) -> list[dict]:
        return [dict(f) for f in self._facts]

    def clear(self) -> dict:
        self._facts.clear()
        return {"status": "cleared", "count": 0}

    def size(self) -> int:
        return len(self._facts)
