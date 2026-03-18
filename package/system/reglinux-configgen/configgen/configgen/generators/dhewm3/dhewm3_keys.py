"""Evmapy controller mappings for dhewm3 (Doom 3 engine).

This module defines button mappings for dhewm3 games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.dhewm3 import dhewm3_keys
    config = dhewm3_keys.get_config()

"""

from typing import Any

# Evmapy configuration for dhewm3 controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
        {
            "trigger": ["hotkey", "pageup"],
            "type": "key",
            "target": ["KEY_F12"],
            "description": "Screenshot",
        },
        {
            "trigger": ["hotkey", "y"],
            "type": "key",
            "target": ["KEY_F5"],
            "description": "Quick Save",
        },
        {
            "trigger": ["hotkey", "x"],
            "type": "key",
            "target": ["KEY_F9"],
            "description": "Quick Load",
        },
    ],
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for dhewm3.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
