from core.cognitive_loop import CognitiveLoop


class FakeCognitivePipeline:

    def __init__(self, results=None):
        self.results = list(results or [])
        self.calls = []

    def run_with_actual(
        self,
        actual,
        text=None,
        voice=None,
        image=None,
        video=None
    ):
        self.calls.append({
            "actual": actual,
            "text": text,
            "voice": voice,
            "image": image,
            "video": video
        })

        if self.results:
            return self.results.pop(0)

        return {
            "status": "completed",
            "difference": 0
        }


def test_loop_configuration():
    pipeline = FakeCognitivePipeline()
    loop = CognitiveLoop(
        pipeline=pipeline,
        max_cycles=5
    )

    config = loop.get_configuration()

    assert config["pipeline"] == "FakeCognitivePipeline"
    assert config["max_cycles"] == 5
    assert config["stopped"] is False
    assert config["history_size"] == 0


def test_invalid_max_cycles():
    pipeline = FakeCognitivePipeline()

    try:
        CognitiveLoop(
            pipeline=pipeline,
            max_cycles=0
        )
        assert False
    except ValueError:
        assert True

    try:
        CognitiveLoop(
            pipeline=pipeline,
            max_cycles=-1
        )
        assert False
    except ValueError:
        assert True

    try:
        CognitiveLoop(
            pipeline=pipeline,
            max_cycles="10"
        )
        assert False
    except ValueError:
        assert True


def test_run_cycle_calls_pipeline():
    pipeline = FakeCognitivePipeline()

    loop = CognitiveLoop(
        pipeline=pipeline,
        max_cycles=5
    )

    result = loop.run_cycle(
        actual=10,
        text="hello"
    )

    assert result["status"] == "completed"
    assert len(pipeline.calls) == 1
    assert pipeline.calls[0]["actual"] == 10
    assert pipeline.calls[0]["text"] == "hello"
    assert len(loop.get_history()) == 1


def test_run_is_bounded_by_max_cycles():
    pipeline = FakeCognitivePipeline()

    loop = CognitiveLoop(
        pipeline=pipeline,
        max_cycles=3
    )

    result = loop.run(
        actual=10,
        text="test"
    )

    assert result["status"] == "completed"
    assert result["cycles_completed"] == 3
    assert result["max_cycles"] == 3
    assert len(result["results"]) == 3
    assert len(pipeline.calls) == 3
    assert len(loop.get_history()) == 3


def test_run_stops_when_cycle_fails():
    pipeline = FakeCognitivePipeline(
        results=[
            {
                "status": "completed",
                "difference": 1
            },
            {
                "status": "failed",
                "reason": "test_failure"
            },
            {
                "status": "completed",
                "difference": 0
            }
        ]
    )

    loop = CognitiveLoop(
        pipeline=pipeline,
        max_cycles=10
    )

    result = loop.run(
        actual=10
    )

    assert result["status"] == "failed"
    assert result["cycles_completed"] == 2
    assert len(result["results"]) == 2
    assert len(pipeline.calls) == 2


def test_stop_prevents_cycle():
    pipeline = FakeCognitivePipeline()

    loop = CognitiveLoop(
        pipeline=pipeline,
        max_cycles=5
    )

    loop.stop()

    result = loop.run_cycle(
        actual=10
    )

    assert result["status"] == "stopped"
    assert result["reason"] == "stop_requested"
    assert len(pipeline.calls) == 0
    assert len(loop.get_history()) == 0


def test_reset_stop_allows_cycle():
    pipeline = FakeCognitivePipeline()

    loop = CognitiveLoop(
        pipeline=pipeline,
        max_cycles=5
    )

    loop.stop()

    assert loop.is_stopped() is True

    loop.reset_stop()

    assert loop.is_stopped() is False

    result = loop.run_cycle(
        actual=10
    )

    assert result["status"] == "completed"
    assert len(pipeline.calls) == 1


def test_clear_history():
    pipeline = FakeCognitivePipeline()

    loop = CognitiveLoop(
        pipeline=pipeline,
        max_cycles=2
    )

    loop.run(
        actual=10
    )

    assert len(loop.get_history()) == 2

    loop.clear_history()

    assert len(loop.get_history()) == 0


def test_run_passes_multimodal_inputs():
    pipeline = FakeCognitivePipeline()

    loop = CognitiveLoop(
        pipeline=pipeline,
        max_cycles=1
    )

    result = loop.run(
        actual=20,
        text="hello",
        voice="audio",
        image="image",
        video="video"
    )

    assert result["status"] == "completed"
    assert len(pipeline.calls) == 1

    call = pipeline.calls[0]

    assert call["actual"] == 20
    assert call["text"] == "hello"
    assert call["voice"] == "audio"
    assert call["image"] == "image"
    assert call["video"] == "video"


def test_run_adds_cycle_numbers():
    pipeline = FakeCognitivePipeline()

    loop = CognitiveLoop(
        pipeline=pipeline,
        max_cycles=3
    )

    result = loop.run(
        actual=5
    )

    assert result["results"][0]["cycle"] == 1
    assert result["results"][1]["cycle"] == 2
    assert result["results"][2]["cycle"] == 3
