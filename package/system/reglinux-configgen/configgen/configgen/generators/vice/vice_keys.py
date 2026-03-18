"""Evmapy controller mappings for VICE.

This module defines button mappings for VICE (Commodore emulator) games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.vice import vice_keys
    config = vice_keys.get_config()

"""

from typing import Any

# Evmapy configuration for VICE controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for VICE.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
