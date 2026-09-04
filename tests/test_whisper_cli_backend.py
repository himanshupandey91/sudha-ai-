"""
Sudha AI - Whisper.cpp CLI Backend Tests

Version 0.1

Tests the whisper.cpp CLI adapter without
requiring a real Whisper installation or model.
"""

from pathlib import Path

import pytest

from core.whisper_cli_backend import (
    WhisperCLIBackend
)


def create_fake_executable(tmp_path):
    path = tmp_path / "whisper-cli"

    path.write_text(
        "fake executable",
        encoding="utf-8"
    )

    return path


def create_fake_model(tmp_path):
    path = tmp_path / "model.bin"

    path.write_bytes(
        b"fake-model"
    )

    return path


def create_fake_audio(tmp_path):
    path = tmp_path / "audio.wav"

    path.write_bytes(
        b"fake-audio"
    )

    return path


def test_backend_accepts_valid_configuration(
    tmp_path
):
    executable = create_fake_executable(
        tmp_path
    )

    model = create_fake_model(
        tmp_path
    )

    backend = WhisperCLIBackend(
        executable_path=str(executable),
        model_path=str(model)
    )

    assert backend.executable_path == str(
        executable
    )

    assert backend.model_path == str(
        model
    )


def test_backend_configuration_detection(
    tmp_path
):
    executable = create_fake_executable(
        tmp_path
    )

    model = create_fake_model(
        tmp_path
    )

    backend = WhisperCLIBackend(
        executable_path=str(executable),
        model_path=str(model)
    )

    assert backend.is_configured() is True


def test_backend_reports_missing_configuration(
    tmp_path
):
    backend = WhisperCLIBackend(
        executable_path=str(
            tmp_path / "missing-cli"
        ),
        model_path=str(
            tmp_path / "missing-model.bin"
        )
    )

    assert backend.is_configured() is False


def test_backend_rejects_invalid_executable_path():
    with pytest.raises(TypeError):

        WhisperCLIBackend(
            executable_path=123,
            model_path="model.bin"
        )


def test_backend_rejects_empty_executable_path():
    with pytest.raises(ValueError):

        WhisperCLIBackend(
            executable_path="",
            model_path="model.bin"
        )


def test_backend_rejects_invalid_model_path():
    with pytest.raises(TypeError):

        WhisperCLIBackend(
            executable_path="whisper-cli",
            model_path=123
        )


def test_backend_rejects_empty_model_path():
    with pytest.raises(ValueError):

        WhisperCLIBackend(
            executable_path="whisper-cli",
            model_path=""
        )


def test_backend_rejects_invalid_timeout():
    with pytest.raises(TypeError):

        WhisperCLIBackend(
            executable_path="whisper-cli",
            model_path="model.bin",
            timeout_seconds="120"
        )


def test_backend_rejects_zero_timeout():
    with pytest.raises(ValueError):

        WhisperCLIBackend(
            executable_path="whisper-cli",
            model_path="model.bin",
            timeout_seconds=0
        )


def test_backend_rejects_missing_audio(
    tmp_path
):
    executable = create_fake_executable(
        tmp_path
    )

    model = create_fake_model(
        tmp_path
    )

    backend = WhisperCLIBackend(
        executable_path=str(executable),
        model_path=str(model)
    )

    with pytest.raises(FileNotFoundError):

        backend.transcribe(
            str(
                tmp_path / "missing.wav"
            )
        )


def test_backend_rejects_missing_executable(
    tmp_path
):
    model = create_fake_model(
        tmp_path
    )

    audio = create_fake_audio(
        tmp_path
    )

    backend = WhisperCLIBackend(
        executable_path=str(
            tmp_path / "missing-cli"
        ),
        model_path=str(model)
    )

    with pytest.raises(FileNotFoundError):

        backend.transcribe(
            str(audio)
        )


def test_backend_rejects_missing_model(
    tmp_path
):
    executable = create_fake_executable(
        tmp_path
    )

    audio = create_fake_audio(
        tmp_path
    )

    backend = WhisperCLIBackend(
        executable_path=str(executable),
        model_path=str(
            tmp_path / "missing-model.bin"
        )
    )

    with pytest.raises(FileNotFoundError):

        backend.transcribe(
            str(audio)
        )


def test_backend_rejects_invalid_audio_type(
    tmp_path
):
    executable = create_fake_executable(
        tmp_path
    )

    model = create_fake_model(
        tmp_path
    )

    backend = WhisperCLIBackend(
        executable_path=str(executable),
        model_path=str(model)
    )

    with pytest.raises(TypeError):

        backend.transcribe(
            123
        )


def test_backend_rejects_empty_audio_path(
    tmp_path
):
    executable = create_fake_executable(
        tmp_path
    )

    model = create_fake_model(
        tmp_path
    )

    backend = WhisperCLIBackend(
        executable_path=str(executable),
        model_path=str(model)
    )

    with pytest.raises(ValueError):

        backend.transcribe(
            ""
        )


def test_backend_extracts_timestamped_output(
    tmp_path
):
    executable = create_fake_executable(
        tmp_path
    )

    model = create_fake_model(
        tmp_path
    )

    backend = WhisperCLIBackend(
        executable_path=str(executable),
        model_path=str(model)
    )

    output = """
    [00:00:00.000 --> 00:00:02.000] Hello Sudha
    [00:00:02.000 --> 00:00:04.000] How are you
    """

    result = backend._extract_text(
        output
    )

    assert result == (
        "Hello Sudha How are you"
    )


def test_backend_extracts_plain_output(
    tmp_path
):
    executable = create_fake_executable(
        tmp_path
    )

    model = create_fake_model(
        tmp_path
    )

    backend = WhisperCLIBackend(
        executable_path=str(executable),
        model_path=str(model)
    )

    output = """
    Hello
    Sudha AI
    """

    result = backend._extract_text(
        output
    )

    assert result == (
        "Hello Sudha AI"
    )


def test_backend_rejects_empty_output(
    tmp_path
):
    executable = create_fake_executable(
        tmp_path
    )

    model = create_fake_model(
        tmp_path
    )

    backend = WhisperCLIBackend(
        executable_path=str(executable),
        model_path=str(model)
    )

    with pytest.raises(RuntimeError):

        backend._extract_text(
            ""
        )
