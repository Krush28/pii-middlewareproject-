"""
Detection Merger

Combines detections from Presidio and Llama
into one consistent entity list.
"""

from typing import List

from .detector import Detection


def merge_detections(
    detections: List[Detection],
) -> List[Detection]:

    if not detections:
        return []

    # Sort by:
    # 1. start position
    # 2. longer entity first
    # 3. higher confidence
    detections = sorted(
        detections,
        key=lambda d: (
            d.start,
            -(d.end - d.start),
            -d.score,
        ),
    )

    merged = []

    for current in detections:

        overlap = False

        for existing in merged:

            if (
                current.start < existing.end
                and current.end > existing.start
            ):

                overlap = True

                # Keep higher confidence detection.
                if current.score > existing.score:
                    merged.remove(existing)
                    merged.append(current)

                break

        if not overlap:
            merged.append(current)

    return sorted(
        merged,
        key=lambda d: d.start,
    )