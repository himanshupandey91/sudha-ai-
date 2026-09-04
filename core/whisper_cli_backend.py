"""
Sudha AI - Whisper.cpp CLI Backend

Version 0.3

Provides an adapter between Sudha AI and the
local whisper.cpp command-line executable.

Architecture:

Audio File
    ↓
WhisperCLIBackend
    ↓
whisper-cli
    ↓
Local Whisper Model
    ↓
Transcribed Text

Version 0.3:
- Supports real local whisper.cpp execution.
- Validates executable, model and audio paths.
- Uses subprocess without shell execution.
- Supports configurable timeout.
- Preserves transcribe() compatibility.
- Provides transcribe_file().
- Provides deterministic output parsing.
- No automatic model downloads.
- No network access.

Design goals:
- Local/offline inference
- Explicit configuration
- Controlled subprocess execution
- Deterministic errors
- Replaceable backend architecture
"""


from pathlib import Path
import subprocess


class WhisperCLIBackend:

    def __init__(
        self,
        executable_path,
        model_path,
        timeout_seconds=120
    ):
        """
        Initialize the local whisper.cpp backend.

        executable_path:
            Path to the whisper.cpp CLI executable.

        model_path:
            Path to the local Whisper model file.

        timeout_seconds:
            Maximum allowed inference time.
        """

        if not isinstance(
            executable_path,
            (str, Path)
        ):
            raise TypeError(
                "executable_path must be a string or Path"
            )

        if str(executable_path).strip() == "":
            raise ValueError(
                "executable_path cannot be empty"
            )

        if not isinstance(
            model_path,
            (str, Path)
        ):
            raise TypeError(
                "model_path must be a string or Path"
            )

        if str(model_path).strip() == "":
            raise ValueError(
                "model_path cannot be empty"
            )

        if not isinstance(
            timeout_seconds,
            (int, float)
        ):
            raise TypeError(
                "timeout_seconds must be a number"
            )

        if timeout_seconds <= 0:
            raise ValueError(
                "timeout_seconds must be greater than zero"
            )

        self.executable_path = Path(
            executable_path
        )

        self.model_path = Path(
            model_path
        )

        self.timeout_seconds = timeout_seconds

    def is_configured(self):
        """
        Return True when both the Whisper CLI
        executable and model file exist.
        """

        return (
            self.executable_path.is_file()
            and self.model_path.is_file()
        )

    def transcribe(self, audio_file):
        """
        Backward-compatible transcription API.

        Delegates to transcribe_file().
        """

        return self.transcribe_file(
            audio_file
        )

    def transcribe_file(self, audio_file):
        """
        Transcribe a local audio file.

        No shell is used.
        No model is downloaded.
        """

        self._validate_audio_file(
            audio_file
        )

        if not self.executable_path.is_file():
            raise FileNotFoundError(
                "whisper_cli_executable_not_found"
            )

        if not self.model_path.is_file():
            raise FileNotFoundError(
                "whisper_model_not_found"
            )

        audio_path = Path(
            audio_file
        )

        command = [
            str(self.executable_path),
            "-m",
            str(self.model_path),
            "-f",
            str(audio_path),
            "-nt",
        ]

        try:

            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
                shell=False
            )

        except subprocess.TimeoutExpired as error:

            raise TimeoutError(
                "whisper_cli_timeout"
            ) from error

        except OSError as error:

            raise RuntimeError(
                "whisper_cli_execution_failed"
            ) from error

        if result.returncode != 0:

            error_message = (
                result.stderr.strip()
                or result.stdout.strip()
                or "unknown_whisper_cli_error"
            )

            raise RuntimeError(
                error_message
            )

        output = result.stdout.strip()

        if output == "":
            raise RuntimeError(
                "whisper_cli_returned_empty_output"
            )

        return self._extract_text(
            output
        )

    def _validate_audio_file(
        self,
        audio_file
    ):
        """
        Validate the supplied audio file.
        """

        if not isinstance(
            audio_file,
            (str, Path)
        ):
            raise TypeError(
                "audio_file must be a string or Path"
            )

        if str(audio_file).strip() == "":
            raise ValueError(
                "audio_file cannot be empty"
            )

        audio_path = Path(
            audio_file
        )

        if not audio_path.is_file():
            raise FileNotFoundError(
                "audio_file_not_found"
            )

    def _extract_text(
        self,
        output
    ):
        """
        Extract transcription text from
        whisper.cpp CLI output.

        Removes timestamp prefixes such as:

            [00:00:00.000 --> 00:00:02.000]

        while preserving normal text.
        """

        if not isinstance(
            output,
            str
        ):
            raise TypeError(
                "output must be a string"
            )

        lines = output.splitlines()

        text_lines = []

        for line in lines:

            cleaned = line.strip()

            if cleaned == "":
                continue

            if cleaned.startswith("["):

                closing = cleaned.find("]")

                if closing != -1:

                    cleaned = (
                        cleaned[
                            closing + 1:
                        ].strip()
                    )

            if cleaned == "":
                continue

            text_lines.append(
                cleaned
            )

        if not text_lines:

            raise RuntimeError(
                "whisper_cli_transcription_empty"
            )

        return " ".join(
            text_lines
        )
