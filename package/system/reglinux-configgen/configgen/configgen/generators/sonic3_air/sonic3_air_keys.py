"""Evmapy controller mappings for SONIC3_AIR (SONIC3_AIR).

This module defines button mappings for SONIC3_AIR games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.sonic3_air import evmapy_sonic3_air
    config = evmapy_sonic3_air.get_config()

"""

from typing import Any

# Evmapy configuration for SONIC3_AIR controller
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
    """Return the evmapy configuration for SONIC3_AIR.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
