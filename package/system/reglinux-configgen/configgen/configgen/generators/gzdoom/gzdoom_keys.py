"""Evmapy controller mappings for GZDOOM (GZDOOM).

This module defines button mappings for GZDOOM games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.gzdoom import evmapy_gzdoom
    config = evmapy_gzdoom.get_config()

"""

from typing import Any

# Evmapy configuration for GZDOOM controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {"trigger": "up", "type": "key", "target": "KEY_UP"},
        {"trigger": "down", "type": "key", "target": "KEY_DOWN"},
        {"trigger": "left", "type": "key", "target": "KEY_LEFT"},
        {"trigger": "right", "type": "key", "target": "KEY_RIGHT"},
        {"trigger": "start", "type": "key", "target": "KEY_ESC"},
        {"trigger": "select", "type": "key", "target": "KEY_TAB"},
        {"trigger": "joystick2", "type": "mouse"},
        {"trigger": "joystick1up", "type": "key", "target": "KEY_W"},
        {"trigger": "joystick1down", "type": "key", "target": "KEY_S"},
        {"trigger": "joystick1left", "type": "key", "target": "KEY_A"},
        {"trigger": "joystick1right", "type": "key", "target": "KEY_D"},
        {"trigger": "b", "type": "key", "target": "KEY_SPACE"},
        {"trigger": "x", "type": "key", "target": "KEY_R"},
        {"trigger": "y", "type": "key", "target": "BTN_LEFT"},
        {"trigger": "a", "type": "key", "target": "KEY_E"},
        {"trigger": "l2", "type": "key", "target": "KEY_LEFTSHIFT"},
        {"trigger": "r2", "type": "key", "target": "BTN_LEFT"},
        {"trigger": "r3", "type": "key", "target": "KEY_END"},
        {"trigger": "l3", "type": "key", "target": "KEY_LEFTCTRL"},
        {"trigger": "pagedown", "type": "key", "target": "KEY_PAGEDOWN"},
        {"trigger": "pageup", "type": "key", "target": "KEY_PAGEUP"},
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
        {
            "trigger": ["hotkey", "y"],
            "type": "key",
            "target": "KEY_F6",
            "description": "quicksave",
        },
        {
            "trigger": ["hotkey", "x"],
            "type": "key",
            "target": "KEY_F9",
            "description": "quickload",
        },
        {
            "trigger": ["hotkey", "pageup"],
            "type": "key",
            "target": "KEY_SYSRQ",
            "description": "screenshot",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for GZDOOM.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
