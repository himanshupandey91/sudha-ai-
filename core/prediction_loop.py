"""
Sudha AI - Prediction Loop

Connects:

Observation
→ Prediction
→ Difference
→ Memory
→ Memory Retrieval
→ Attention
→ Learning
→ Curiosity
→ World Model
→ Goal Generation
→ Planning
→ Action
"""

from core.prediction import PredictionEngine
from core.difference import DifferenceEngine
from core.memory import MemoryEngine
from core.attention import AttentionEngine
from core.learning import LearningEngine
from core.curiosity import CuriosityEngine
from core.world_model import WorldModel
from core.goal import GoalEngine
from core.planning import PlanningEngine
from core.action import ActionEngine


class PredictionLoop:

    def __init__(self):
        self.predictor = PredictionEngine()
        self.difference_engine = DifferenceEngine()
        self.memory = MemoryEngine()
        self.attention = AttentionEngine()
        self.learning = LearningEngine()
        self.curiosity = CuriosityEngine()
        self.world_model = WorldModel()
        self.goal = GoalEngine()
        self.planning = PlanningEngine()
        self.action = ActionEngine()

    def process(self, observation, actual):
        """
        Execute one complete Sudha AI cycle.

        Flow:

        Observation
        → Prediction
        → Difference
        → Memory Store
        → Memory Retrieval
        → Attention
        → Learning
        → Curiosity
        → World Model
        → Goal
        → Planning
        → Action
        """

        # 1. Prediction
        prediction = self.predictor.predict(observation)

        # 2. Difference
        difference = self.difference_engine.calculate(
            prediction,
            actual
        )

        # 3. Create structured experience
        experience = {
            "observation": observation,
            "prediction": prediction,
            "actual": actual,
            "difference": difference
        }

        # 4. Store experience in memory
        memory_store = self.memory.store(
            experience
        )

        # 5. Retrieve memories with equal or greater
        # prediction error
        memory_retrieval = self.memory.retrieve_by_difference(
            difference
        )

        # 6. Attention
        attention_state = self.attention.focus(
            experience
        )

        # 7. Learning
        learning_state = self.learning.learn(
            difference
        )

        # 8. Curiosity
        curiosity_state = self.curiosity.calculate(
            difference
        )

        # 9. World Model
        state = self.world_model.update(
            observation=observation,
            prediction=prediction,
            actual=actual,
            difference=difference
        )

        # 10. Goal Generation
        goal_state = self.goal.generate(
            state
        )

        # 11. Planning
        planning_state = self.planning.create_plan(
            goal_state
        )

        # 12. Action
        action_context = {
            "observation": observation,
            "prediction": prediction,
            "actual": actual
        }

        action_state = self.action.execute_plan(
            planning_state["plan"],
            context=action_context
        )

        # Add higher-level states
        state["memory"] = {
            "store": memory_store,
            "retrieved": memory_retrieval,
            "total_memories": self.memory.size()
        }

        state["attention"] = attention_state
        state["learning"] = learning_state
        state["curiosity"] = curiosity_state
        state["goal"] = goal_state
        state["planning"] = planning_state
        state["action"] = action_state

        return state
