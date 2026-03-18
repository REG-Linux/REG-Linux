"""Evmapy controller mappings for CDOGS (CDOGS).

This module defines button mappings for CDOGS games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.cdogs import evmapy_cdogs
    config = evmapy_cdogs.get_config()

"""

from typing import Any

# Evmapy configuration for CDOGS controller
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
    """Return the evmapy configuration for CDOGS.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
