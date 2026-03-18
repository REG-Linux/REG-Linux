"""Evmapy controller mappings for SONIC_MANIA (SONIC_MANIA).

This module defines button mappings for SONIC_MANIA games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.sonic_mania import evmapy_sonic_mania
    config = evmapy_sonic_mania.get_config()

"""

from typing import Any

# Evmapy configuration for SONIC_MANIA controller
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
    """Return the evmapy configuration for SONIC_MANIA.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
