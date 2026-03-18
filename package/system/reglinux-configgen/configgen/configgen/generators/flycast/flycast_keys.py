"""Evmapy controller mappings for FLYCAST.

This module defines button mappings for FLYCAST games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.flycast import flycast_keys
    config = flycast_keys.get_config()

"""

from typing import Any

# Evmapy configuration for FLYCAST controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
        {
            "trigger": ["hotkey", "b"],
            "type": "key",
            "target": ["KEY_RIGHTSHIFT", "KEY_F12"],
            "description": "Hide the bezel",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for FLYCAST.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
