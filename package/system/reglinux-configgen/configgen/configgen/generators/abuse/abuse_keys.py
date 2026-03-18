"""Evmapy controller mappings for ABUSE (ABUSE).

This module defines button mappings for ABUSE games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.abuse import evmapy_abuse
    config = evmapy_abuse.get_config()

"""

from typing import Any

# Evmapy configuration for ABUSE controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
        {"trigger": "joystick1", "type": "mouse"},
        {"trigger": "l2", "type": "key", "target": "BTN_LEFT"},
        {"trigger": "r2", "type": "key", "target": "BTN_RIGHT"},
        {"trigger": "up", "type": "key", "target": "KEY_UP"},
        {"trigger": "down", "type": "key", "target": "KEY_DOWN"},
        {"trigger": "left", "type": "key", "target": "KEY_LEFT"},
        {"trigger": "right", "type": "key", "target": "KEY_RIGHT"},
        {"trigger": "start", "type": "key", "target": "KEY_ENTER"},
        {"trigger": "select", "type": "key", "target": "KEY_ESC"},
        {"trigger": "b", "type": "key", "target": "BTN_LEFT"},
        {"trigger": "a", "type": "key", "target": "KEY_UP"},
        {"trigger": "pageup", "type": "key", "target": "KEY_RIGHTCTRL"},
        {"trigger": "pagedown", "type": "key", "target": "KEY_INSERT"},
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for ABUSE.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
