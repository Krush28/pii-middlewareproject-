from middleware.detector import Detection
from middleware.sanitizer import SanitizationPolicy


def test_sanitization_policy():

    policy = SanitizationPolicy()

    detection = Detection(
        entity_type="PERSON",
        value="Aarav Mehta",
        start=11,
        end=22,
        score=0.99,
        detector="Presidio",
    )

    assert policy.should_sanitize(detection)


def test_non_pii_entity():

    policy = SanitizationPolicy()

    detection = Detection(
        entity_type="JOB_TITLE",
        value="Engineer",
        start=0,
        end=8,
        score=0.99,
        detector="Presidio",
    )

    assert not policy.should_sanitize(detection)