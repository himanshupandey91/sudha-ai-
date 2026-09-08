"""
Sudha AI - Hierarchical Memory Tests

Step 64-B

Tests:
- exact matching
- multi-field matching
- memory-layer filtering
- result limits
- copy isolation
- invalid retrieval arguments
- legacy storage APIs
"""

import pytest

from core.hierarchical_memory import HierarchicalMemory


class TestHierarchicalMemoryRetrieval:

    def setup_method(self):
        self.memory = HierarchicalMemory(
            working_size=5,
            episodic_size=10,
            semantic_size=10,
            procedural_size=10,
        )

    def test_episodic_matching_returns_matching_records(self):
        self.memory.store_episodic({
            "topic": "physics",
            "result": "success",
        })

        self.memory.store_episodic({
            "topic": "biology",
            "result": "success",
        })

        result = self.memory.retrieve_episodic_matching({
            "topic": "physics",
        })

        assert len(result) == 1
        assert result[0]["topic"] == "physics"

    def test_matching_supports_multiple_fields(self):
        self.memory.store_semantic({
            "topic": "physics",
            "status": "verified",
            "value": 42,
        })

        self.memory.store_semantic({
            "topic": "physics",
            "status": "unverified",
            "value": 42,
        })

        result = self.memory.retrieve_semantic_matching({
            "topic": "physics",
            "status": "verified",
        })

        assert len(result) == 1
        assert result[0]["status"] == "verified"

    def test_non_matching_record_is_not_returned(self):
        self.memory.store_procedural({
            "process": "prediction",
            "status": "success",
        })

        result = self.memory.retrieve_procedural_matching({
            "process": "learning",
        })

        assert result == []

    def test_retrieve_matching_can_filter_memory_types(self):
        self.memory.store_episodic({
            "topic": "physics",
            "source": "episode",
        })

        self.memory.store_semantic({
            "topic": "physics",
            "source": "semantic",
        })

        result = self.memory.retrieve_matching(
            {"topic": "physics"},
            memory_types=["semantic"],
        )

        assert set(result.keys()) == {"semantic"}
        assert len(result["semantic"]) == 1
        assert result["semantic"][0]["source"] == "semantic"

    def test_retrieve_matching_can_search_multiple_memory_types(self):
        self.memory.store_episodic({
            "topic": "physics",
            "source": "episode",
        })

        self.memory.store_semantic({
            "topic": "physics",
            "source": "semantic",
        })

        result = self.memory.retrieve_matching(
            {"topic": "physics"},
            memory_types=["episodic", "semantic"],
        )

        assert set(result.keys()) == {
            "episodic",
            "semantic",
        }

        assert len(result["episodic"]) == 1
        assert len(result["semantic"]) == 1

        assert result["episodic"][0]["source"] == "episode"
        assert result["semantic"][0]["source"] == "semantic"

    def test_limit_returns_latest_matching_records(self):
        self.memory.store_episodic({
            "topic": "physics",
            "id": 1,
        })

        self.memory.store_episodic({
            "topic": "physics",
            "id": 2,
        })

        self.memory.store_episodic({
            "topic": "physics",
            "id": 3,
        })

        result = self.memory.retrieve_episodic_matching(
            {"topic": "physics"},
            limit=2,
        )

        assert len(result) == 2
        assert [record["id"] for record in result] == [2, 3]

    def test_zero_limit_returns_empty_result(self):
        self.memory.store_episodic({
            "topic": "physics",
            "id": 1,
        })

        result = self.memory.retrieve_episodic_matching(
            {"topic": "physics"},
            limit=0,
        )

        assert result == []

    def test_empty_criteria_matches_all_records(self):
        self.memory.store_episodic({
            "id": 1,
        })

        self.memory.store_episodic({
            "id": 2,
        })

        result = self.memory.retrieve_episodic_matching({})

        assert len(result) == 2

    def test_returned_records_are_copies(self):
        self.memory.store_semantic({
            "topic": "physics",
            "value": 42,
        })

        result = self.memory.retrieve_semantic_matching({
            "topic": "physics",
        })

        result[0]["value"] = 999

        stored = self.memory.retrieve_semantic()

        assert stored[0]["value"] == 42

    def test_invalid_criteria_is_rejected(self):
        with pytest.raises(TypeError):
            self.memory.retrieve_matching(
                ["physics"],
            )

    def test_invalid_memory_types_is_rejected(self):
        with pytest.raises(TypeError):
            self.memory.retrieve_matching(
                {"topic": "physics"},
                memory_types="semantic",
            )

    def test_unknown_memory_type_is_rejected(self):
        with pytest.raises(ValueError):
            self.memory.retrieve_matching(
                {"topic": "physics"},
                memory_types=["unknown"],
            )

    def test_non_integer_limit_is_rejected(self):
        with pytest.raises(TypeError):
            self.memory.retrieve_matching(
                {"topic": "physics"},
                limit=1.5,
            )

    def test_negative_limit_is_rejected(self):
        with pytest.raises(ValueError):
            self.memory.retrieve_matching(
                {"topic": "physics"},
                limit=-1,
            )

    def test_legacy_storage_and_retrieval_still_work(self):
        self.memory.store_working({
            "state": "active",
        })

        result = self.memory.retrieve_working()

        assert result == [
            {
                "state": "active",
            }
        ]
