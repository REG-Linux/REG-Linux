"""Evmapy controller mappings for Ruffle.

This module defines button mappings for Ruffle games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.ruffle import ruffle_keys
    config = ruffle_keys.get_config()

"""

from typing import Any

# Evmapy configuration for Ruffle controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
        {"trigger": "joystick2", "type": "mouse"},
        {"trigger": "l2", "type": "key", "target": "BTN_LEFT"},
        {"trigger": "r2", "type": "key", "target": "BTN_RIGHT"},
        {"trigger": "up", "type": "key", "target": "KEY_UP"},
        {"trigger": "down", "type": "key", "target": "KEY_DOWN"},
        {"trigger": "left", "type": "key", "target": "KEY_LEFT"},
        {"trigger": "right", "type": "key", "target": "KEY_RIGHT"},
        {"trigger": "b", "type": "key", "target": "KEY_5"},
        {"trigger": "start", "type": "key", "target": "KEY_1"},
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for Ruffle.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
