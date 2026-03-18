"""Evmapy controller mappings for EASYRPG (EASYRPG).

This module defines button mappings for EASYRPG games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.easyrpg import evmapy_easyrpg
    config = evmapy_easyrpg.get_config()

"""

from typing import Any

# Evmapy configuration for EASYRPG controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {"trigger": "up", "type": "key", "target": "KEY_UP"},
        {"trigger": "down", "type": "key", "target": "KEY_DOWN"},
        {"trigger": "left", "type": "key", "target": "KEY_LEFT"},
        {"trigger": "right", "type": "key", "target": "KEY_RIGHT"},
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
        {"trigger": ["hotkey", "a"], "type": "key", "target": ["KEY_F12"]},
        {"trigger": ["hotkey", "y"], "type": "key", "target": ["KEY_F11"]},
        {"trigger": ["hotkey", "b"], "type": "key", "target": ["KEY_F9"]},
        {"trigger": ["hotkey", "pageup"], "type": "key", "target": ["KEY_F7"]},
        {"trigger": ["hotkey", "right"], "type": "key", "target": ["KEY_F"]},
        {"trigger": ["pagedown"], "type": "key", "target": ["KEY_LEFTCTRL"]},
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for EASYRPG.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
