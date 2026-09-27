"""
Placeholder Engine

Replaces detected PII with deterministic placeholders
and stores the mapping required for restoration.
"""

from typing import Dict, List, Tuple

from .detector import Detection


class PlaceholderEngine:

    def __init__(self):
        self.mapping: Dict[str, str] = {}
        self.counters: Dict[str, int] = {}

    def _create_placeholder(
        self,
        entity_type: str,
    ) -> str:

        entity_type = entity_type.upper()

        self.counters[entity_type] = (
            self.counters.get(entity_type, 0) + 1
        )

        return (
            f"<<PII_{entity_type}_"
            f"{self.counters[entity_type]:03d}>>"
        )

    def sanitize(
        self,
        text: str,
        detections: List[Detection],
    ) -> Tuple[str, Dict[str, str]]:

        self.mapping = {}
        self.counters = {}

        # Process from right to left so offsets remain valid.
        detections = sorted(
            detections,
            key=lambda d: d.start,
            reverse=True,
        )

        sanitized = text

        for detection in detections:

            placeholder = self._create_placeholder(
                detection.entity_type
            )

            sanitized = (
                sanitized[:detection.start]
                + placeholder
                + sanitized[detection.end:]
            )

            self.mapping[placeholder] = detection.value

        return sanitized, dict(self.mapping)