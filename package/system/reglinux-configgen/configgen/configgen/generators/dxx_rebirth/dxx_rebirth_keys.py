"""Evmapy controller mappings for DXX_REBIRTH (DXX_REBIRTH).

This module defines button mappings for DXX_REBIRTH games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.dxx_rebirth import evmapy_dxx_rebirth
    config = evmapy_dxx_rebirth.get_config()

"""

from typing import Any

# Evmapy configuration for DXX_REBIRTH controller
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
    """Return the evmapy configuration for DXX_REBIRTH.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
