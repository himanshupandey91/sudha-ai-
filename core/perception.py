"""
Sudha AI - Multimodal Perception Layer

Version 0.2

The Perception Layer is the entry point for
multimodal information.

Supported input types:
- text
- voice
- image
- video

Version 0.2:
- Validates incoming perception data.
- Converts different modalities into a
  common structured representation.
- Creates unified observations.
- Supports multiple observations in one cycle.
- Preserves source modality information.
- Does NOT perform AI inference.

Design goals:
- Deterministic behavior
- Explicit input validation
- Common multimodal representation
- Unified observation structure
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
        Process voice/audio input.

        Speech recognition can be connected
        above this layer.
        """

        return self.perceive(
            "voice",
            audio
        )

    def perceive_image(self, image):
        """
        Process image input.

        Computer vision can be connected
        above this layer.
        """

        return self.perceive(
            "image",
            image
        )

    def perceive_video(self, video):
        """
        Process video input.
        """

        return self.perceive(
            "video",
            video
        )

    def create_observation(
        self,
        perceptions
    ):
        """
        Combine multiple perceived inputs
        into one unified observation.

        Example:

            text + voice + image + video

        becomes one structured observation
        that can be passed to downstream
        cognitive components.
        """

        if not isinstance(
            perceptions,
            list
        ):
            return {
                "status": "rejected",
                "reason": "perceptions_must_be_a_list"
            }

        if len(perceptions) == 0:
            return {
                "status": "rejected",
                "reason": "perceptions_cannot_be_empty"
            }

        valid_perceptions = []

        for perception in perceptions:

            if not isinstance(
                perception,
                dict
            ):
                return {
                    "status": "rejected",
                    "reason": "perception_must_be_a_dictionary"
                }

            if perception.get("status") != "perceived":
                return {
                    "status": "rejected",
                    "reason": "invalid_perception"
                }

            modality = perception.get(
                "modality"
            )

            if modality not in self.ALLOWED_MODALITIES:
                return {
                    "status": "rejected",
                    "reason": "invalid_perception_modality"
                }

            if "data" not in perception:
                return {
                    "status": "rejected",
                    "reason": "perception_data_missing"
                }

            valid_perceptions.append(
                perception
            )

        modalities = [
            perception["modality"]
            for perception in valid_perceptions
        ]

        data = {
            perception["modality"]:
                perception["data"]
            for perception in valid_perceptions
        }

        return {
            "status": "observation_created",
            "modalities": modalities,
            "data": data,
            "count": len(valid_perceptions)
        }

    def create_multimodal_observation(
        self,
        text=None,
        voice=None,
        image=None,
        video=None
    ):
        """
        Convenience method for creating a
        unified observation directly from
        multimodal inputs.

        Only supplied inputs are included.
        """

        perceptions = []

        if text is not None:
            perceptions.append(
                self.perceive_text(text)
            )

        if voice is not None:
            perceptions.append(
                self.perceive_voice(voice)
            )

        if image is not None:
            perceptions.append(
                self.perceive_image(image)
            )

        if video is not None:
            perceptions.append(
                self.perceive_video(video)
            )

        return self.create_observation(
            perceptions
                                   )
