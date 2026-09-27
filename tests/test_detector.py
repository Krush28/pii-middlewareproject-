from middleware.detector import PIIDetector


def test_detector_initialization():

    detector = PIIDetector(
        use_presidio=False,
        use_llama=False,
    )

    assert detector is not None