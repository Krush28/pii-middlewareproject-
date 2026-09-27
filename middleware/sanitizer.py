"""
PII Sanitization Policy

Determines which detected entities should be
replaced before the text is sent to GPT.
"""

from typing import List

from .detector import Detection


DEFAULT_BLOCKED_TYPES = {
    "PERSON",
    "EMAIL_ADDRESS",
    "EMAIL",
    "PHONE_NUMBER",
    "PHONE",
    "LOCATION",
    "ADDRESS",
    "DATE_TIME",
    "DATE",
    "IP_ADDRESS",
    "PASSPORT",
    "DRIVER_LICENSE",
    "NATIONAL_ID",
    "CUSTOMER_ID",
    "EMPLOYEE_ID",
    "ACCOUNT_ID",
    "TICKET_ID",
}


class SanitizationPolicy:

    def __init__(
        self,
        blocked_types=None,
    ):

        self.blocked_types = (
            set(blocked_types)
            if blocked_types
            else DEFAULT_BLOCKED_TYPES
        )

    def should_sanitize(
        self,
        detection: Detection,
    ) -> bool:

        return (
            detection.entity_type.upper()
            in self.blocked_types
        )

    def filter(
        self,
        detections: List[Detection],
    ) -> List[Detection]:

        return [
            detection
            for detection in detections
            if self.should_sanitize(detection)
        ]