"""Evmapy controller mappings for FALLOUT2 (FALLOUT2).

This module defines button mappings for FALLOUT2 games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.fallout2 import evmapy_fallout2
    config = evmapy_fallout2.get_config()

"""

from typing import Any

# Evmapy configuration for FALLOUT2 controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
        {
            "trigger": ["hotkey", "b"],
            "type": "key",
            "target": "KEY_ESC",
            "description": "Bring up menu",
        },
        {
            "trigger": ["hotkey", "y"],
            "type": "key",
            "target": "KEY_F6",
            "description": "Quick save",
        },
        {
            "trigger": ["hotkey", "x"],
            "type": "key",
            "target": "KEY_F7",
            "description": "Quick load",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for FALLOUT2.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
