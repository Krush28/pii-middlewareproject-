"""
PII Detection Layer

Combines:
    1. Microsoft Presidio
    2. Llama-based PII detection

The detector returns a common entity format so the
rest of the middleware does not care which detector
found the entity.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Detection:
    entity_type: str
    value: str
    start: int
    end: int
    score: float
    detector: str


class PIIDetector:

    def __init__(
        self,
        use_presidio: bool = True,
        use_llama: bool = True,
    ):
        self.use_presidio = use_presidio
        self.use_llama = use_llama

        self.analyzer = None

        if self.use_presidio:
            self._load_presidio()

    def _load_presidio(self):
        """Load Microsoft Presidio."""

        try:
            from presidio_analyzer import AnalyzerEngine

            self.analyzer = AnalyzerEngine()

        except ImportError:
            raise ImportError(
                "Presidio is not installed. "
                "Install it with: pip install presidio-analyzer"
            )

    def detect_with_presidio(self, text: str) -> List[Detection]:

        if self.analyzer is None:
            return []

        results = self.analyzer.analyze(
            text=text,
            language="en",
        )

        detections = []

        for result in results:

            value = text[result.start:result.end]

            detections.append(
                Detection(
                    entity_type=result.entity_type,
                    value=value,
                    start=result.start,
                    end=result.end,
                    score=float(result.score),
                    detector="Presidio",
                )
            )

        return detections

    def detect_with_llama(self, text: str) -> List[Detection]:
        """
        Llama detector placeholder.

        This will be connected to llama_pii_test.py
        after we stabilize the Llama JSON extraction.
        """

        return []

    def detect(self, text: str) -> List[Detection]:

        detections = []

        if self.use_presidio:
            detections.extend(
                self.detect_with_presidio(text)
            )

        if self.use_llama:
            detections.extend(
                self.detect_with_llama(text)
            )

        return detections