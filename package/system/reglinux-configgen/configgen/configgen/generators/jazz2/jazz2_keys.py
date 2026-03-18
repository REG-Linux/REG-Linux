"""Evmapy controller mappings for JAZZ2 (JAZZ2).

This module defines button mappings for JAZZ2 games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.jazz2 import evmapy_jazz2
    config = evmapy_jazz2.get_config()

"""

from typing import Any

# Evmapy configuration for JAZZ2 controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
            "description": "Exit game",
        }
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for JAZZ2.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
