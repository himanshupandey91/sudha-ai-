"""
Sudha AI - Memory Engine

Version 0.5

Provides bounded structured memory for Sudha AI.

Capabilities:
- Store experiences
- Retrieve all memories
- Retrieve recent memories
- Retrieve memories by prediction difference
- Backward-compatible max_memories configuration
- Preserve learning signals
- Bounded memory size
- Deterministic behavior
- No external side effects
"""


class MemoryEngine:

    def __init__(
        self,
        max_size=100,
        max_memories=None
    ):
        """
        Initialize memory.

        max_size:
            New configuration name.

        max_memories:
            Backward-compatible configuration name.
        """

        if max_memories is not None:

            if not isinstance(
                max_memories,
                int
            ):
                raise TypeError(
                    "max_memories must be an integer"
                )

            max_size = max_memories

        if not isinstance(
            max_size,
            int
        ):
            raise TypeError(
                "max_size must be an integer"
            )

        if max_size <= 0:
            raise ValueError(
                "max_size must be greater than zero"
            )

        self.max_size = max_size

        # Backward-compatible attribute.
        self.max_memories = max_size

        self._memories = []

    def store(self, memory):
        """
        Store one structured memory.
        """

        if not isinstance(
            memory,
            dict
        ):
            return {
                "status": "rejected",
                "reason": "memory_must_be_a_dictionary"
            }

        stored_memory = dict(memory)

        self._memories.append(
            stored_memory
        )

        if len(
            self._memories
        ) > self.max_size:

            self._memories.pop(0)

        return {
            "status": "stored",
            "memory": dict(
                stored_memory
            ),
            "count": len(
                self._memories
            ),
            "memory_size": len(
                self._memories
            )
        }

    def retrieve(self):
        """
        Retrieve all stored memories.
        """

        return [
            dict(memory)
            for memory in self._memories
        ]

    def retrieve_all(self):
        """
        Backward-compatible alias
        for retrieving all memories.
        """

        return self.retrieve()

    def retrieve_recent(
        self,
        count
    ):
        """
        Retrieve the most recent memories.
        """

        if not isinstance(
            count,
            int
        ):
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

    def retrieve_by_difference(
        self,
        minimum_difference
    ):
        """
        Retrieve memories whose prediction
        difference is greater than or equal
        to the requested threshold.
        """

        if not isinstance(
            minimum_difference,
            (int, float)
        ):
            raise TypeError(
                "minimum_difference must be a number"
            )

        results = []

        for memory in self._memories:

            difference = memory.get(
                "difference"
            )

            if isinstance(
                difference,
                (int, float)
            ):

                if difference >= minimum_difference:

                    results.append(
                        dict(memory)
                    )

        return results

    def retrieve_by_error(
        self,
        minimum_error=0
    ):
        """
        Newer alias for retrieving memories
        by prediction error.
        """

        return self.retrieve_by_difference(
            minimum_error
        )

    def clear(self):
        """
        Clear all memories.
        """

        self._memories.clear()

        return {
            "status": "cleared",
            "memory_size": 0
        }

    def size(self):
        """
        Return the current number of memories.
        """

        return len(
            self._memories
        )

    def get_configuration(self):
        """
        Return memory configuration.
        """

        return {
            "max_size": self.max_size,
            "max_memories": self.max_memories,
            "current_size": len(
                self._memories
            )
        }
