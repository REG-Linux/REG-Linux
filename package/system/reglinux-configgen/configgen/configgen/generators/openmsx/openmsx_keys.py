"""Evmapy controller mappings for OpenMSX.

This module defines button mappings for OpenMSX games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.openmsx import openmsx_keys
    config = openmsx_keys.get_config()

"""

from typing import Any

# Evmapy configuration for OpenMSX controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
        {"trigger": ["pageup"], "type": "key", "target": ["KEY_F5"]},
        {"trigger": ["hotkey", "x"], "type": "key", "target": ["KEY_F6"]},
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for OpenMSX.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
