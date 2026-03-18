"""Evmapy controller mappings for RPCS3.

This module defines button mappings for RPCS3 (PS3 emulator) games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.rpc s3 import rpcs3_keys
    config = rpcs3_keys.get_config()

"""

from typing import Any

# Evmapy configuration for RPCS3 controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
            "description": "Exit emulator",
        },
        {
            "trigger": ["hotkey", "select"],
            "type": "key",
            "target": "KEY_F8",
            "description": "Fullscreen toggle",
        },
        {
            "trigger": ["hotkey", "pageup"],
            "type": "key",
            "target": "KEY_F10",
            "description": "Screenshot",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for RPCS3.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
