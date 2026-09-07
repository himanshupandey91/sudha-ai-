"""
Sudha AI - Hierarchical Memory

Version 0.1

Memory hierarchy:

Working Memory
    ↓
Episodic Memory
    ↓
Semantic Memory
    ↓
Procedural Memory

Design goals:
- Keep memory types separated.
- Keep every memory bounded.
- Preserve insertion order.
- Return copies instead of internal objects.
- Deterministic behavior.
- No fake learning.
- No external side effects.
"""


class HierarchicalMemory:

    MEMORY_TYPES = (
        "working",
        "episodic",
        "semantic",
        "procedural",
    )

    def __init__(
        self,
        working_size=10,
        episodic_size=100,
        semantic_size=100,
        procedural_size=100,
    ):
        self._validate_size(
            working_size,
            "working_size",
        )
        self._validate_size(
            episodic_size,
            "episodic_size",
        )
        self._validate_size(
            semantic_size,
            "semantic_size",
        )
        self._validate_size(
            procedural_size,
            "procedural_size",
        )

        self.working_size = working_size
        self.episodic_size = episodic_size
        self.semantic_size = semantic_size
        self.procedural_size = procedural_size

        self._working = []
        self._episodic = []
        self._semantic = []
        self._procedural = []

    def _validate_size(self, size, name):
        if not isinstance(size, int):
            raise TypeError(
                f"{name} must be an integer"
            )

        if size <= 0:
            raise ValueError(
                f"{name} must be greater than zero"
            )

    def _store(
        self,
        storage,
        maximum_size,
        memory,
    ):
        if not isinstance(memory, dict):
            return {
                "status": "rejected",
                "reason": "memory_must_be_a_dictionary",
            }

        stored_memory = dict(memory)

        storage.append(stored_memory)

        if len(storage) > maximum_size:
            storage.pop(0)

        return {
            "status": "stored",
            "memory": dict(stored_memory),
            "memory_size": len(storage),
        }

    def _retrieve(self, storage):
        return [
            dict(memory)
            for memory in storage
        ]

    def store_working(self, memory):
        return self._store(
            self._working,
            self.working_size,
            memory,
        )

    def store_episodic(self, memory):
        return self._store(
            self._episodic,
            self.episodic_size,
            memory,
        )

    def store_semantic(self, memory):
        return self._store(
            self._semantic,
            self.semantic_size,
            memory,
        )

    def store_procedural(self, memory):
        return self._store(
            self._procedural,
            self.procedural_size,
            memory,
        )

    def retrieve_working(self):
        return self._retrieve(
            self._working
        )

    def retrieve_episodic(self):
        return self._retrieve(
            self._episodic
        )

    def retrieve_semantic(self):
        return self._retrieve(
            self._semantic
        )

    def retrieve_procedural(self):
        return self._retrieve(
            self._procedural
        )

    def retrieve_all(self):
        return {
            "working": self.retrieve_working(),
            "episodic": self.retrieve_episodic(),
            "semantic": self.retrieve_semantic(),
            "procedural": self.retrieve_procedural(),
        }

    def size(self, memory_type=None):
        if memory_type is None:
            return (
                len(self._working)
                + len(self._episodic)
                + len(self._semantic)
                + len(self._procedural)
            )

        if memory_type == "working":
            return len(self._working)

        if memory_type == "episodic":
            return len(self._episodic)

        if memory_type == "semantic":
            return len(self._semantic)

        if memory_type == "procedural":
            return len(self._procedural)

        raise ValueError(
            "unknown_memory_type"
        )

    def clear(self, memory_type=None):
        if memory_type is None:
            self._working.clear()
            self._episodic.clear()
            self._semantic.clear()
            self._procedural.clear()

            return {
                "status": "cleared",
                "memory_size": 0,
            }

        if memory_type == "working":
            self._working.clear()

        elif memory_type == "episodic":
            self._episodic.clear()

        elif memory_type == "semantic":
            self._semantic.clear()

        elif memory_type == "procedural":
            self._procedural.clear()

        else:
            raise ValueError(
                "unknown_memory_type"
            )

        return {
            "status": "cleared",
            "memory_type": memory_type,
            "memory_size": self.size(memory_type),
        }

    def get_configuration(self):
        return {
            "working_size": self.working_size,
            "episodic_size": self.episodic_size,
            "semantic_size": self.semantic_size,
            "procedural_size": self.procedural_size,
            "working_current_size": len(self._working),
            "episodic_current_size": len(self._episodic),
            "semantic_current_size": len(self._semantic),
            "procedural_current_size": len(self._procedural),
            "total_size": self.size(),
        }
