"""
Sudha AI - Audio Input Foundation

Version 0.1

Provides a controlled foundation for audio input.

This layer:
- Validates audio input
- Stores audio metadata
- Does not perform speech recognition yet
- Does not access microphone hardware yet
- Has no network access
- Has no external side effects

Speech recognition will be connected in a later version.
"""


class AudioEngine:

    SUPPORTED_FORMATS = {
        "wav",
        "pcm",
        "raw"
    }

    def __init__(self, sample_rate=16000, channels=1):
        """
        Initialize the audio engine.

        sample_rate:
            Audio sampling rate in Hz.

        channels:
            Number of audio channels.
        """

        if not isinstance(sample_rate, int):
            raise TypeError(
                "sample_rate must be an integer"
            )

        if sample_rate <= 0:
            raise ValueError(
                "sample_rate must be greater than zero"
            )

        if not isinstance(channels, int):
            raise TypeError(
                "channels must be an integer"
            )

        if channels <= 0:
            raise ValueError(
                "channels must be greater than zero"
            )

        self.sample_rate = sample_rate
        self.channels = channels

    def validate(self, audio_data):
        """
        Validate incoming audio data.
        """

        if audio_data is None:
            return {
                "status": "rejected",
                "reason": "audio_data_cannot_be_none"
            }

        if not isinstance(
            audio_data,
            (bytes, bytearray)
        ):
            return {
                "status": "rejected",
                "reason": "audio_data_must_be_bytes"
            }

        if len(audio_data) == 0:
            return {
                "status": "rejected",
                "reason": "audio_data_cannot_be_empty"
            }

        return {
            "status": "valid",
            "size": len(audio_data),
            "sample_rate": self.sample_rate,
            "channels": self.channels
        }

    def create_audio_input(
        self,
        audio_data,
        audio_format="raw"
    ):
        """
        Convert validated audio into a
        common internal representation.
        """

        validation = self.validate(
            audio_data
        )

        if validation["status"] != "valid":
            return validation

        if audio_format not in self.SUPPORTED_FORMATS:
            return {
                "status": "rejected",
                "reason": "audio_format_not_supported",
                "audio_format": audio_format
            }

        return {
            "status": "received",
            "format": audio_format,
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "size": len(audio_data),
            "data": bytes(audio_data)
        }

    def get_configuration(self):
        """
        Return the current audio configuration.
        """

        return {
            "sample_rate": self.sample_rate,
            "channels": self.channels,
            "supported_formats": sorted(
                self.SUPPORTED_FORMATS
            )
        }
