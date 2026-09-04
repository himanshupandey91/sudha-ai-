"""
Sudha AI - Perception Layer

Version 0.1

The Perception Layer is the entry point for
multimodal information.

Supported input types:
- text
- voice
- image
- video

Version 0.1:
- Validates incoming perception data.
- Converts different modalities into a
  common structured representation.
- Does NOT perform speech recognition or
  computer vision yet.

Design goals:
- Deterministic behavior
- Explicit input validation
- Common multimodal representation
- No external side effects
- Fully testable
"""


class PerceptionEngine:

    ALLOWED_MODALITIES = {
        "text",
        "voice",
        "image",
        "video",
    }

    def perceive(self, modality, data):
        """
        Convert an input into a common perception structure.
        """

        if not isinstance(modality, str):
            return {
                "status": "rejected",
                "reason": "modality_must_be_a_string"
            }

        if modality not in self.ALLOWED_MODALITIES:
            return {
                "status": "rejected",
                "reason": "modality_not_supported",
                "modality": modality
            }

        if data is None:
            return {
                "status": "rejected",
                "reason": "data_cannot_be_none"
            }

        return {
            "status": "perceived",
            "modality": modality,
            "data": data
        }

    def perceive_text(self, text):
        """
        Process text input.
        """

        return self.perceive(
            "text",
            text
        )

    def perceive_voice(self, audio):
        """
        Accept voice/audio input.

        Speech recognition will be connected
        in a later version.
        """

        return self.perceive(
            "voice",
            audio
        )

    def perceive_image(self, image):
        """
        Accept image input.

        Computer vision will be connected
        in a later version.
        """

        return self.perceive(
            "image",
            image
        )

    def perceive_video(self, video):
        """
        Accept video input.

        Real-time video processing will be
        connected in a later version.
        """

        return self.perceive(
            "video",
            video
        )
