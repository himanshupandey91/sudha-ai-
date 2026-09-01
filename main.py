"""
Sudha AI
Version: 0.1

Initial research prototype.
"""


class SudhaAI:
    def __init__(self):
        self.memory = []

    def observe(self, input_data):
        """Receive an observation."""
        return input_data

    def remember(self, information):
        """Store information in memory."""
        self.memory.append(information)

    def run(self, input_data):
        observation = self.observe(input_data)
        self.remember(observation)

        return {
            "observation": observation,
            "memory_size": len(self.memory)
        }


if __name__ == "__main__":
    ai = SudhaAI()

    result = ai.run("Hello, Sudha AI")

    print(result)
