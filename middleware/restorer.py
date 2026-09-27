"""
Placeholder Restorer

Restores original PII values into the response
received from GPT.
"""

from typing import Dict


def restore_placeholders(
    text: str,
    mapping: Dict[str, str],
) -> str:

    restored = text

    for placeholder, original_value in mapping.items():

        restored = restored.replace(
            placeholder,
            original_value,
        )

    return restored