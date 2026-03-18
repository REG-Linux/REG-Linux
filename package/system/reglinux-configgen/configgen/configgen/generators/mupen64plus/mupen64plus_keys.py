"""Evmapy controller mappings for Mupen64plus.

This module defines button mappings for Mupen64plus games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.mupen64plus import MUPEN64PLUS_keys
    config = MUPEN64PLUS_keys.get_config()

"""

from typing import Any

# Evmapy configuration for Mupen64plus controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": "KEY_ESC",
            "description": "Exit the emulator",
        },
        {
            "trigger": ["hotkey", "y"],
            "type": "key",
            "target": "KEY_F5",
            "description": "Save emulator state",
        },
        {
            "trigger": ["hotkey", "x"],
            "type": "key",
            "target": "KEY_F7",
            "description": "Load emulator state",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for Mupen64plus.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
