"""
Sudha AI - Experience Learning Engine

Version 0.4

Connects:

Prediction
    ↓
Hierarchical Memory Retrieval
    ↓
Actual Outcome
    ↓
Difference
    ↓
Learning Signal
    ↓
Memory Update
    ↓
World Model

Version 0.4:
- Preserves existing MemoryEngine API
- Integrates HierarchicalMemory into prediction
- Retrieves relevant episodic experience before prediction
- Stores completed experiences in episodic memory
- Stores learned knowledge in semantic memory
- Stores learning procedure information in procedural memory
- Keeps AdaptivePredictionEngine compatible
- Never invents actual outcomes
- Deterministic behavior
- No external side effects
"""

from core.difference import DifferenceEngine
from core.learning import LearningEngine
from core.adaptive_prediction import AdaptivePredictionEngine
from core.memory import MemoryEngine
from core.hierarchical_memory import HierarchicalMemory
from core.world_model import WorldModel


class ExperienceLearningEngine:

    def __init__(
        self,
        adaptive_prediction=None,
        difference=None,
        learning=None,
        memory=None,
        hierarchical_memory=None,
        world_model=None
    ):
        """
        Initialize the experience-learning system.

        MemoryEngine remains the compatibility memory.

        HierarchicalMemory is now also connected directly
        to AdaptivePredictionEngine so previous episodic
        experiences can influence future predictions.
        """

        self.memory = (
            memory
            if memory is not None
            else MemoryEngine()
        )

        self.hierarchical_memory = (
            hierarchical_memory
            if hierarchical_memory is not None
            else HierarchicalMemory()
        )

        self.adaptive_prediction = (
            adaptive_prediction
            if adaptive_prediction is not None
            else AdaptivePredictionEngine(
                memory_engine=self.memory,
                hierarchical_memory=self.hierarchical_memory
            )
        )

        self.difference = (
            difference
            if difference is not None
            else DifferenceEngine()
        )

        self.learning = (
            learning
            if learning is not None
            else LearningEngine()
        )

        self.world_model = (
            world_model
            if world_model is not None
            else WorldModel()
        )

    def predict(self, observation):
        """
        Generate a prediction using:

        1. Base prediction
        2. Relevant hierarchical memory
        3. Compatibility memory
        4. Adaptive prediction
        """

        prediction = self.adaptive_prediction.predict(
            observation
        )

        return {
            "status": "predicted",
            "observation": observation,
            "prediction": prediction
        }

    def learn(
        self,
        observation,
        prediction,
        actual
    ):
        """
        Learn from an explicitly supplied actual outcome.

        The actual outcome is never generated internally.

        The completed experience is stored in:

        1. Compatibility MemoryEngine
        2. Episodic hierarchical memory
        3. Semantic hierarchical memory
        4. Procedural hierarchical memory
        5. World Model
        """

        difference = self.difference.calculate(
            prediction,
            actual
        )

        learning_result = self.learning.learn(
            difference
        )

        memory_result = self.adaptive_prediction.remember(
            observation=observation,
            prediction=prediction,
            actual=actual,
            difference=difference,
            learning=learning_result
        )

        experience = {
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": difference,
            "learning": learning_result
        }

        episodic_result = (
            self.hierarchical_memory.store_episodic(
                experience
            )
        )

        semantic_memory = {
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": difference,
            "learning_signal": learning_result.get(
                "learning_signal"
            )
        }

        semantic_result = (
            self.hierarchical_memory.store_semantic(
                semantic_memory
            )
        )

        procedural_memory = {
            "process": "prediction_difference_learning",
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": difference,
            "learning": learning_result
        }

        procedural_result = (
            self.hierarchical_memory.store_procedural(
                procedural_memory
            )
        )

        world_model_result = (
            self.world_model.update(
                observation=observation,
                prediction=prediction,
                actual=actual,
                difference=difference,
                learning=learning_result
            )
        )

        hierarchical_result = {
            "status": "stored",
            "episodic": episodic_result,
            "semantic": semantic_result,
            "procedural": procedural_result
        }

        return {
            "status": "learned",
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": difference,
            "learning": learning_result,
            "memory": memory_result,
            "hierarchical_memory": hierarchical_result,
            "world_model": world_model_result
        }

    def run(
        self,
        observation,
        actual=None
    ):
        """
        Run one complete experience-learning cycle.

        Without actual:

            observation → prediction

        With actual:

            observation
                ↓
            hierarchical memory retrieval
                ↓
            prediction
                ↓
            actual
                ↓
            difference
                ↓
            learning
                ↓
            memory update
                ↓
            world model
        """

        prediction_result = self.predict(
            observation
        )

        if prediction_result["status"] != "predicted":
            return prediction_result

        prediction = prediction_result[
            "prediction"
        ]

        if actual is None:
            return {
                "status": "predicted",
                "observation": observation,
                "prediction": prediction
            }

        learning_result = self.learn(
            observation=observation,
            prediction=prediction,
            actual=actual
        )

        return {
            "status": "completed",
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": learning_result[
                "difference"
            ],
            "learning": learning_result[
                "learning"
            ],
            "memory": learning_result[
                "memory"
            ],
            "hierarchical_memory": learning_result[
                "hierarchical_memory"
            ],
            "world_model": learning_result[
                "world_model"
            ]
        }

    def get_memory(self):
        """
        Return the compatibility memory.

        This preserves the previous API.
        """

        return self.memory.retrieve()

    def get_memory_size(self):
        """
        Return the number of stored compatibility memories.
        """

        return self.memory.size()

    def get_hierarchical_memory(self):
        """
        Return all hierarchical memory layers.
        """

        return self.hierarchical_memory.retrieve_all()

    def get_hierarchical_memory_size(
        self,
        memory_type=None
    ):
        """
        Return hierarchical memory size.

        If memory_type is None:
            return total size.

        Otherwise return the size of the
        requested memory layer.
        """

        return self.hierarchical_memory.size(
            memory_type
        )

    def get_world_state(self):
        """
        Return the current World Model state.
        """

        return self.world_model.get_state()

    def get_world_history(self):
        """
        Return World Model history.
        """

        return self.world_model.get_history()

    def get_experience_count(self):
        """
        Return the number of experiences
        recorded by the World Model.
        """

        return self.world_model.get_experience_count()

    def clear_memory(self):
        """
        Clear both compatibility memory and
        hierarchical memory, then reset the
        World Model.
        """

        memory_result = self.memory.clear()

        hierarchical_result = (
            self.hierarchical_memory.clear()
        )

        world_result = self.world_model.clear()

        return {
            "status": "cleared",
            "memory": memory_result,
            "hierarchical_memory": hierarchical_result,
            "world_model": world_result
        }

    def get_configuration(self):
        """
        Return the current engine configuration.
        """

        return {
            "memory": type(
                self.memory
            ).__name__,
            "hierarchical_memory": type(
                self.hierarchical_memory
            ).__name__,
            "adaptive_prediction": type(
                self.adaptive_prediction
            ).__name__,
            "difference": type(
                self.difference
            ).__name__,
            "learning": type(
                self.learning
            ).__name__,
            "world_model": type(
                self.world_model
            ).__name__
        }
