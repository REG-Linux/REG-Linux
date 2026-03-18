"""Evmapy controller mappings for shadPS4.

This module defines button mappings for shadPS4 games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.shadps4 import shadps4_keys
    config = shadps4_keys.get_config()

"""

from typing import Any

# Evmapy configuration for shadPS4 controller
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
    """Return the evmapy configuration for shadPS4.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
