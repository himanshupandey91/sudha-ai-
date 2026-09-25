cat << 'EOF' > core/answer_engine.py
import json
import os
from typing import Any, Dict, List, Optional

class AnswerEngine:
    """
    Sudha AI Knowledge & QA Engine.
    Handles question answering, pattern matching, and autonomous learning.
    """
    def __init__(self, persistence_path: str = "data/knowledge.json"):
        self.persistence_path = persistence_path
        self.knowledge: Dict[str, Dict[str, Any]] = {}
        
        default_facts = {
            "hello": "Namaste! Main Sudha AI hoon. Aapka swagat hai.",
            "hi": "Namaste! Kaise madad kar sakti hoon?",
            "namaste": "Namaste! Main Sudha AI hoon. Aap mujhse koi bhi sawal poochh sakte hain.",
            "tumhara naam kya hai": "Mera naam Sudha AI hai.",
            "tum kaun ho": "Main Sudha AI hoon, ek autonomous cognitive AI system.",
            "tumhe kisne banaya": "Mujhe Himanshu Pandey ne develop kiya hai.",
            "tum kya kar sakti ho": "Main sawalon ke jawab de sakti hoon, autonomous reasoning loop chala sakti hoon, aur aapse naye facts seekh sakti hoon.",
            "tum abhi kya kar sakte hi": "Main sawalon ke jawab de sakti hoon, aur agar mujhe koi jawab nahi pata toh aap mujhe sikha sakte hain!"
        }
        self._load_knowledge(default_facts)

    def _load_knowledge(self, default_facts: Dict[str, str]):
        if os.path.exists(self.persistence_path):
            try:
                with open(self.persistence_path, "r", encoding="utf-8") as f:
                    self.knowledge = json.load(f)
                    return
            except Exception:
                pass
        
        for q, a in default_facts.items():
            self.knowledge[q.lower().strip()] = {
                "answer": a,
                "keywords": q.lower().split()[:5]
            }
        self._save_knowledge()

    def _save_knowledge(self):
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def answer(self, question: str) -> Dict[str, Any]:
        if not question or not isinstance(question, str):
            return {"status": "rejected", "reason": "invalid_question", "confidence": 0.0}

        clean_q = question.lower().strip().rstrip("?!.,")

        # 1. Exact Match
        if clean_q in self.knowledge:
            return {
                "status": "known",
                "answer": self.knowledge[clean_q]["answer"],
                "confidence": 1.0
            }

        # 2. Substring & Keyword Matching
        q_words = set(clean_q.split())
        best_match = None
        best_score = 0.0

        for stored_q, data in self.knowledge.items():
            stored_words = set(stored_q.split())
            overlap = len(q_words.intersection(stored_words))
            if overlap > 0:
                score = overlap / max(len(stored_words), len(q_words))
                if score > best_score and score >= 0.4:
                    best_score = score
                    best_match = data["answer"]

        if best_match:
            return {
                "status": "known",
                "answer": best_match,
                "confidence": round(best_score, 2)
            }

        # 3. Unknown
        return {
            "status": "unknown",
            "answer": "Mujhe abhi iska jawab nahi pata.",
            "confidence": 0.0
        }

    def add_knowledge(self, question: str, answer: str, keywords: Optional[List[str]] = None):
        clean_q = question.lower().strip().rstrip("?!.,")
        if not clean_q or not answer:
            return

        if keywords is None:
            keywords = clean_q.split()[:5]

        self.knowledge[clean_q] = {
            "answer": answer.strip(),
            "keywords": keywords
        }
        self._save_knowledge()
EOF
