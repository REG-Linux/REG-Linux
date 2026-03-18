"""Evmapy controller mappings for odcommander (Odin Commander).

This module defines button mappings for odcommander games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.odcommander import odcommander_keys
    config = odcommander_keys.get_config()

"""

from typing import Any

# Evmapy configuration for odcommander controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
    ],
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for odcommander.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
