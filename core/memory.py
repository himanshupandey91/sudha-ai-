"""
Sudha AI - Memory Engine

Version 0.1

Stores and retrieves structured experiences.

Design goals:
- Structured memory
- Deterministic behavior
- Bounded memory size
- Retrieval by similarity
- No external side effects
"""


class MemoryEngine:

    def __init__(self, max_memories=1000):
        """
        Initialize memory.

        max_memories:
            Maximum number of experiences stored.
        """

        if not isinstance(max_memories, int):
            raise TypeError("max_memories must be an integer")

        if max_memories <= 0:
            raise ValueError("max_memories must be greater than zero")

        self.max_memories = max_memories
        self.memories = []

    def store(self, experience):
        """
        Store one structured experience.

        The newest experience is kept.
        If memory exceeds the limit, the oldest
        experience is removed.
        """

        if not isinstance(experience, dict):
            raise TypeError("experience must be a dictionary")

        self.memories.append(experience.copy())

        if len(self.memories) > self.max_memories:
            self.memories.pop(0)

        return {
            "status": "stored",
            "memory_size": len(self.memories)
        }

    def retrieve_all(self):
        """
        Return all stored memories.
        """

        return [memory.copy() for memory in self.memories]

    def retrieve_recent(self, count=1):
        """
        Return the most recent memories.
        """

        if not isinstance(count, int):
            raise TypeError("count must be an integer")

        if count < 0:
            raise ValueError("count cannot be negative")

        return [
            memory.copy()
            for memory in self.memories[-count:]
        ]

    def retrieve_by_difference(self, minimum_difference):
        """
        Retrieve memories whose prediction error
        is greater than or equal to the supplied threshold.
        """

        if not isinstance(minimum_difference, (int, float)):
            raise TypeError(
                "minimum_difference must be numeric"
            )

        results = []

        for memory in self.memories:

            difference = memory.get("difference", 0)

            if difference >= minimum_difference:
                results.append(memory.copy())

        return results

    def size(self):
        """
        Return the current number of stored memories.
        """

        return len(self.memories)

    def clear(self):
        """
        Clear all stored memories.
        """

        self.memories.clear()

        return {
            "status": "cleared",
            "memory_size": 0
        }
