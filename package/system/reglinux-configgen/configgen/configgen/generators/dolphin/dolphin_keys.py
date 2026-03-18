"""Evmapy controller mappings for DOLPHIN.

This module defines button mappings for DOLPHIN games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.dolphin import dolphin_keys
    config = dolphin_keys.get_config()

"""

from typing import Any

# Evmapy configuration for DOLPHIN controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
        {
            "trigger": ["hotkey", "up"],
            "type": "key",
            "target": ["KEY_LEFTSHIFT", "KEY_F1"],
        },
        {
            "trigger": ["hotkey", "down"],
            "type": "key",
            "target": ["KEY_LEFTSHIFT", "KEY_F2"],
        },
        {"trigger": ["hotkey", "y"], "type": "key", "target": "KEY_F5"},
        {"trigger": ["hotkey", "x"], "type": "key", "target": "KEY_F8"},
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for DOLPHIN.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
