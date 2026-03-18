"""Evmapy controller mappings for MOONLIGHT (MOONLIGHT).

This module defines button mappings for MOONLIGHT games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.moonlight import evmapy_moonlight
    config = evmapy_moonlight.get_config()

"""

from typing import Any

# Evmapy configuration for MOONLIGHT controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
            "description": "Exit emulator using SDL",
        }
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for MOONLIGHT.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
