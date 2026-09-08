"""
Sudha AI - Hierarchical Memory / Adaptive Prediction Integration Tests

Step 64-C

Tests real integration between:

HierarchicalMemory
        ↓
AdaptivePredictionEngine
        ↓
Prediction

Coverage:
- HierarchicalMemory connection
- exact observation retrieval
- previous experience influencing prediction
- completed experience persistence
- hierarchical memory priority over legacy MemoryEngine

These tests verify actual behavior rather than placeholder
connection flags.
"""

from core.adaptive_prediction import AdaptivePredictionEngine
from core.experience_learning import ExperienceLearningEngine
from core.hierarchical_memory import HierarchicalMemory
from core.memory import MemoryEngine


class TestHierarchicalMemoryPredictionIntegration:

    def test_hierarchical_memory_is_connected_to_prediction(self):
        """
        AdaptivePredictionEngine should retain and expose the
        supplied HierarchicalMemory instance.
        """

        hierarchical_memory = HierarchicalMemory()

        engine = AdaptivePredictionEngine(
            hierarchical_memory=hierarchical_memory
        )

        assert engine.hierarchical_memory is hierarchical_memory

        configuration = engine.get_configuration()

        assert configuration["hierarchical_memory"] == (
            "HierarchicalMemory"
        )

    def test_previous_experience_is_retrieved_for_same_observation(self):
        """
        An exact observation stored in HierarchicalMemory should
        be found and used by AdaptivePredictionEngine.
        """

        hierarchical_memory = HierarchicalMemory()

        observation = {
            "topic": "physics",
            "state": "test",
        }

        hierarchical_memory.store_episodic({
            "observation": observation,
            "prediction": 10,
            "actual": 20,
            "difference": 10,
        })

        engine = AdaptivePredictionEngine(
            hierarchical_memory=hierarchical_memory
        )

        details = engine.predict_with_details(
            observation
        )

        assert details["experience_used"] is True

        assert details["experience_source"] == (
            "hierarchical_memory"
        )

        assert details["experience"] is not None

        assert details["experience"]["actual"] == 20

    def test_hierarchical_memory_changes_future_prediction(self):
        """
        A previous experience stored in hierarchical memory should
        change the next prediction.

        Base prediction:
            10

        Previous experience:
            prediction = 10
            difference = 10

        Expected adaptive prediction:
            10 + 10 = 20
        """

        hierarchical_memory = HierarchicalMemory()

        observation = {
            "topic": "physics",
            "state": "adaptive",
        }

        hierarchical_memory.store_episodic({
            "observation": observation,
            "prediction": 10,
            "actual": 20,
            "difference": 10,
        })

        engine = AdaptivePredictionEngine(
            hierarchical_memory=hierarchical_memory
        )

        prediction = engine.predict(
            observation
        )

        assert prediction == 20

    def test_hierarchical_memory_contains_completed_experience(self):
        """
        ExperienceLearningEngine should store a completed
        prediction/actual/difference/learning experience in
        HierarchicalMemory.
        """

        hierarchical_memory = HierarchicalMemory()

        engine = ExperienceLearningEngine(
            hierarchical_memory=hierarchical_memory
        )

        observation = {
            "topic": "physics",
            "state": "completed",
        }

        result = engine.run(
            observation=observation,
            actual=20,
        )

        assert result["status"] == "completed"

        memories = (
            hierarchical_memory.retrieve_episodic_matching(
                {
                    "observation": observation
                }
            )
        )

        assert len(memories) == 1

        experience = memories[0]

        assert experience["observation"] == observation
        assert "prediction" in experience
        assert experience["actual"] == 20
        assert "difference" in experience
        assert "learning" in experience

    def test_hierarchical_memory_is_used_before_legacy_memory(self):
        """
        When both memory systems contain experiences for the same
        observation, HierarchicalMemory must take priority.

        Hierarchical experience:
            prediction = 10
            difference = 20
            expected result = 30

        Legacy experience:
            prediction = 10
            difference = 5
            expected result = 15

        Expected prediction:
            30

        This proves the hierarchical memory path is actually
        preferred over the legacy MemoryEngine path.
        """

        hierarchical_memory = HierarchicalMemory()
        legacy_memory = MemoryEngine()

        observation = {
            "topic": "priority",
            "state": "same_observation",
        }

        hierarchical_memory.store_episodic({
            "observation": observation,
            "prediction": 10,
            "actual": 30,
            "difference": 20,
        })

        legacy_memory.store({
            "observation": observation,
            "prediction": 10,
            "actual": 15,
            "difference": 5,
        })

        engine = AdaptivePredictionEngine(
            memory_engine=legacy_memory,
            hierarchical_memory=hierarchical_memory,
        )

        details = engine.predict_with_details(
            observation
        )

        assert details["experience_used"] is True

        assert details["experience_source"] == (
            "hierarchical_memory"
        )

        assert details["prediction"] == 30

        assert details["experience"]["difference"] == 20
