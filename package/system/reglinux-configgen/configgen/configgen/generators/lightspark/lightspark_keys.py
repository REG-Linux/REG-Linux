"""Evmapy controller mappings for Lightspark.

This module defines button mappings for Lightspark games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.lightspark import lightspark_keys
    config = lightspark_keys.get_config()

"""

from typing import Any

# Evmapy configuration for Lightspark controller
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
    """Return the evmapy configuration for Lightspark.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
