"""Evmapy controller mappings for RYUJINX (SWITCH).

This module defines button mappings for SWITCH games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.ryujinx import evmapy_switch
    config = evmapy_switch.get_config()

"""

from typing import Any

# Evmapy configuration for SWITCH controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
            "description": "Exit the emulator",
        }
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for SWITCH.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
