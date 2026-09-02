"""
Sudha AI - Attention Module

Version 0.1

Selects the most important information from the current state.
"""


class AttentionEngine:

    def focus(self, state):
        """
        Identify the most important part of the current state.
        """

        if not state:
            return None

        if state.get("difference", 0) > 0:
            return {
                "focus": "prediction_error",
                "value": state["difference"]
            }

        return {
            "focus": "observation",
            "value": state.get("observation")
        }
