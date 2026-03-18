"""Evmapy controller mappings for Supermodel.

This module defines button mappings for Supermodel (Sega Model 3 emulator) games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.supermodel import supermodel_keys
    config = supermodel_keys.get_config()

"""

from typing import Any

# Evmapy configuration for Supermodel controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_ESC"],
        },
        {
            "trigger": ["hotkey", "a"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_R"],
        },
        {
            "trigger": ["hotkey", "b"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_P"],
        },
        {
            "trigger": ["hotkey", "x"],
            "type": "key",
            "target": ["KEY_F7"],
        },
        {
            "trigger": ["hotkey", "y"],
            "type": "key",
            "target": ["KEY_F5"],
        },
        {
            "trigger": ["hotkey", "up"],
            "type": "key",
            "target": ["KEY_F6"],
        },
        {
            "trigger": ["hotkey", "pageup"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_S"],
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for Supermodel.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
