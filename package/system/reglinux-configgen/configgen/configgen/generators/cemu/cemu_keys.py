"""Evmapy controller mappings for CEMU (Wii U emulator).

This module defines button mappings for CEMU games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.cemu import cemu_keys
    config = cemu_keys.get_config()

"""

from typing import Any

# Evmapy configuration for CEMU controller
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
            "target": "KEY_F10",
            "description": "Screenshot",
        },
        {
            "trigger": ["hotkey", "pageup"],
            "type": "key",
            "target": "KEY_F9",
            "description": "Toggle FPS counter",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for CEMU.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
