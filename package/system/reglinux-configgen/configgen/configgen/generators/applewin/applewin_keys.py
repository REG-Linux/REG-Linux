"""Evmapy controller mappings for APPLEWIN (APPLE2).

This module defines button mappings for APPLE2 games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.applewin import evmapy_apple2
    config = evmapy_apple2.get_config()

"""

from typing import Any

# Evmapy configuration for APPLE2 controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        }
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for APPLE2.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
