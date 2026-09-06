"""
Sudha AI - Memory Engine

Version 0.2

Provides bounded structured memory for Sudha AI.

Capabilities:
- Store experiences
- Retrieve stored experiences
- Preserve learning signals
- Bounded memory size
- Deterministic behavior
- No external side effects
"""


class MemoryEngine:

    def __init__(self, max_size=100):
        """
        Initialize memory.

        max_size:
            Maximum number of memories retained.
        """

        if not isinstance(max_size, int):
            raise TypeError(
                "max_size must be an integer"
            )

        if max_size <= 0:
            raise ValueError(
                "max_size must be greater than zero"
            )

        self.max_size = max_size
        self._memories = []

    def store(self, memory):
        """
        Store one structured memory.
        """

        if not isinstance(memory, dict):
            return {
                "status": "rejected",
                "reason": "memory_must_be_a_dictionary"
            }

        self._memories.append(
            dict(memory)
        )

        if len(self._memories) > self.max_size:
            self._memories.pop(0)

        return {
            "status": "stored",
            "memory": dict(memory),
            "count": len(self._memories)
        }

    def retrieve(self):
        """
        Retrieve all stored memories.

        Returns copies so callers cannot directly
        modify internal memory.
        """

        return [
            dict(memory)
            for memory in self._memories
        ]

    def clear(self):
        """
        Clear all stored memories.
        """

        self._memories.clear()

        return {
            "status": "cleared"
        }

    def size(self):
        """
        Return the current number of memories.
        """

        return len(self._memories)

    def get_configuration(self):
        """
        Return memory configuration.
        """

        return {
            "max_size": self.max_size,
            "current_size": len(self._memories)
        }
