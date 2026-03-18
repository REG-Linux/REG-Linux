"""Evmapy controller mappings for Solarus.

This module defines button mappings for Solarus games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.solarus import solarus_keys
    config = solarus_keys.get_config()

"""

from typing import Any

# Evmapy configuration for Solarus controller
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
    """Return the evmapy configuration for Solarus.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
