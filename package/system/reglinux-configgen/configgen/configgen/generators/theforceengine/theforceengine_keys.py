"""Evmapy controller mappings for THEFORCEENGINE (THEFORCEENGINE).

This module defines button mappings for THEFORCEENGINE games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.theforceengine import evmapy_theforceengine
    config = evmapy_theforceengine.get_config()

"""

from typing import Any

# Evmapy configuration for THEFORCEENGINE controller
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
            "trigger": ["hotkey", "x"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F9"],
            "description": "Quick Load",
        },
        {
            "trigger": ["hotkey", "y"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F5"],
            "description": "Quick Save",
        },
        {
            "trigger": ["hotkey"],
            "type": "key",
            "target": ["KEY_ESC"],
            "description": "Skip cutscene",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for THEFORCEENGINE.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
