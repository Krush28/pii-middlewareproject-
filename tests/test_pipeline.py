from middleware.detector import Detection
from middleware.placeholders import PlaceholderEngine
from middleware.restorer import restore_placeholders


def test_placeholder_and_restoration():

    text = "My name is Aarav Mehta."

    detection = Detection(
        entity_type="PERSON",
        value="Aarav Mehta",
        start=11,
        end=22,
        score=0.99,
        detector="Test",
    )

    engine = PlaceholderEngine()

    sanitized, mapping = engine.sanitize(
        text,
        [detection],
    )

    assert sanitized == (
        "My name is <<PII_PERSON_001>>."
    )

    restored = restore_placeholders(
        sanitized,
        mapping,
    )

    assert restored == text