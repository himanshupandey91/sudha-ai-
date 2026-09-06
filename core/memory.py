"""
Sudha AI - Memory Engine

Version 0.4

Provides bounded structured memory for Sudha AI.

Capabilities:
- Store experiences
- Retrieve all memories
- Retrieve recent memories
- Retrieve high-error experiences
- Backward-compatible API
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

        stored_memory = dict(memory)

        self._memories.append(
            stored_memory
        )

        if len(self._memories) > self.max_size:
            self._memories.pop(0)

        return {
            "status": "stored",
            "memory": dict(stored_memory),
            "count": len(self._memories),
            "memory_size": len(self._memories)
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

    def retrieve_all(self):
        """
        Backward-compatible retrieval method.
        """

        return self.retrieve()

    def retrieve_recent(self, count):
        """
        Retrieve the most recent memories.

        count:
            Number of recent memories requested.
        """

        if not isinstance(count, int):
            raise TypeError(
                "count must be an integer"
            )

        if count < 0:
            raise ValueError(
                "count must be zero or greater"
            )

        if count == 0:
            return []

        return [
            dict(memory)
            for memory in self._memories[-count:]
        ]

    def retrieve_by_error(self, minimum_error=0):
        """
        Retrieve memories whose prediction error
        is greater than or equal to minimum_error.

        Memories without a numeric 'difference'
        field are ignored.
        """

        if not isinstance(
            minimum_error,
            (int, float)
        ):
            raise TypeError(
                "minimum_error must be a number"
            )

        results = []

        for memory in self._memories:

            difference = memory.get(
                "difference"
            )

            if isinstance(
                difference,
                (int, float)
            ) and difference >= minimum_error:

                results.append(
                    dict(memory)
                )

        return results

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
