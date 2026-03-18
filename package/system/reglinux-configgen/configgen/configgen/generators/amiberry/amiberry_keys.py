"""Evmapy controller mappings for AMIBERRY.

This module defines button mappings for AMIBERRY games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.amiberry import amiberry_keys
    config = amiberry_keys.get_config()

"""

from typing import Any

# Evmapy configuration for AMIBERRY controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "b"],
            "type": "key",
            "target": "KEY_F12",
            "description": "Configuration menu",
        },
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": "KEY_ESC",
            "description": "Exit the emulator",
        },
        {"trigger": "joystick2", "type": "mouse"},
        {"trigger": "l2", "type": "key", "target": "BTN_LEFT"},
        {"trigger": "r2", "type": "key", "target": "BTN_RIGHT"},
        {"trigger": "x", "type": "key", "target": "KEY_SPACE"},
        {"trigger": "y", "type": "key", "target": "KEY_ENTER"},
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for AMIBERRY.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
