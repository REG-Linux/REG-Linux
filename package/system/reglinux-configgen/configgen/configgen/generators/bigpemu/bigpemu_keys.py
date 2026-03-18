"""Evmapy controller mappings for BIGPEMU.

This module defines button mappings for BIGPEMU games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.bigpemu import bigpemu_keys
    config = bigpemu_keys.get_config()

"""

from typing import Any

# Evmapy configuration for BIGPEMU controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
            "description": "Exit the emulator",
        },
        {
            "trigger": ["hotkey", "b"],
            "type": "key",
            "target": ["KEY_ESC"],
            "description": "Configuration menu",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for BIGPEMU.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
