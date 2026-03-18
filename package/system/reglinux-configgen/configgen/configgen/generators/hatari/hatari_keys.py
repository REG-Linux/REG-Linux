"""Evmapy controller mappings for HATARI (ATARIST).

This module defines button mappings for ATARIST games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.hatari import evmapy_atarist
    config = evmapy_atarist.get_config()

"""

from typing import Any

# Evmapy configuration for ATARIST controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        }
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for ATARIST.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
