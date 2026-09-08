"""
Sudha AI - Hierarchical Memory Prediction Integration Tests

Step 64-C

Verifies that:

Experience
    ↓
Hierarchical Memory
    ↓
Relevant Memory Retrieval
    ↓
Prediction

is a real executable path.

The tests do not inject fake adaptation flags.
"""

from core.experience_learning import ExperienceLearningEngine


class TestHierarchicalMemoryPredictionIntegration:

    def test_hierarchical_memory_is_connected_to_prediction(self):
        engine = ExperienceLearningEngine()

        configuration = engine.adaptive_prediction.get_configuration()

        assert configuration[
            "hierarchical_memory"
        ] == "HierarchicalMemory"

    def test_previous_experience_is_retrieved_for_same_observation(self):
        engine = ExperienceLearningEngine()

        observation = {
            "value": 10
        }

        engine.run(
            observation=observation,
            actual=20
        )

        details = (
            engine.adaptive_prediction.predict_with_details(
                observation
            )
        )

        assert details[
            "experience_used"
        ] is True

        assert details[
            "experience_source"
        ] == "hierarchical_memory"

    def test_hierarchical_memory_changes_future_prediction(self):
        engine = ExperienceLearningEngine()

        observation = {
            "value": 10
        }

        first = engine.run(
            observation=observation,
            actual=20
        )

        second = engine.run(
            observation=observation
        )

        assert first[
            "prediction"
        ] != second[
            "prediction"
        ]

    def test_hierarchical_memory_contains_completed_experience(self):
        engine = ExperienceLearningEngine()

        observation = {
            "value": 10
        }

        engine.run(
            observation=observation,
            actual=20
        )

        episodic = (
            engine.hierarchical_memory.retrieve_episodic_matching(
                {
                    "observation": observation
                }
            )
        )

        assert len(episodic) == 1

        assert episodic[0][
            "actual"
        ] == 20

    def test_hierarchical_memory_is_used_before_legacy_memory(self):
        engine = ExperienceLearningEngine()

        observation = {
            "value": 10
        }

        engine.run(
            observation=observation,
            actual=20
        )

        details = (
            engine.adaptive_prediction.predict_with_details(
                observation
            )
        )

        assert details[
            "experience_source"
        ] == "hierarchical_memory"
