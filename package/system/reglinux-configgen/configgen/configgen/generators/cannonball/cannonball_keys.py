"""Evmapy controller mappings for CANNONBALL (CANNONBALL).

This module defines button mappings for CANNONBALL games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.cannonball import evmapy_cannonball
    config = evmapy_cannonball.get_config()

"""

from typing import Any

# Evmapy configuration for CANNONBALL controller
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
    """Return the evmapy configuration for CANNONBALL.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
