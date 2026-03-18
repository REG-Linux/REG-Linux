"""Evmapy controller mappings for Xenia.

This module defines button mappings for Xenia (Xbox 360 emulator) games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.xenia import xenia_keys
    config = xenia_keys.get_config()

"""

from typing import Any

# Evmapy configuration for Xenia controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for Xenia.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
