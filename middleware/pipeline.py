"""
PII Middleware Pipeline

Application
    ↓
Detection
    ↓
Merge
    ↓
Sanitization Policy
    ↓
Placeholder Engine
    ↓
SAFE TEXT
    ↓
GPT
    ↓
Placeholder Restoration
    ↓
Application
"""

from .detector import PIIDetector
from .merger import merge_detections
from .sanitizer import SanitizationPolicy
from .placeholders import PlaceholderEngine
from .restorer import restore_placeholders


class PIIMiddleware:

    def __init__(
        self,
        use_presidio=True,
        use_llama=True,
    ):

        self.detector = PIIDetector(
            use_presidio=use_presidio,
            use_llama=use_llama,
        )

        self.policy = SanitizationPolicy()

        self.placeholder_engine = PlaceholderEngine()

    def sanitize(self, text):

        detections = self.detector.detect(text)

        merged = merge_detections(
            detections
        )

        allowed = self.policy.filter(
            merged
        )

        sanitized_text, mapping = (
            self.placeholder_engine.sanitize(
                text,
                allowed,
            )
        )

        return {
            "original_text": text,
            "sanitized_text": sanitized_text,
            "detections": merged,
            "mapping": mapping,
        }

    def restore(
        self,
        response,
        mapping,
    ):

        return restore_placeholders(
            response,
            mapping,
        )