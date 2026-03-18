"""Evmapy controller mappings for PPSSPP (PSP).

This module defines button mappings for PSP games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.ppsspp import evmapy_psp
    config = evmapy_psp.get_config()

"""

from typing import Any

# Evmapy configuration for PSP controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
        {
            "trigger": ["hotkey", "y"],
            "type": "key",
            "target": ["KEY_F3"],
            "description": "Save State",
        },
        {
            "trigger": ["hotkey", "x"],
            "type": "key",
            "target": ["KEY_F4"],
            "description": "Load State",
        },
        {
            "trigger": ["hotkey", "down"],
            "type": "key",
            "target": ["KEY_F5"],
            "description": "Slot -",
        },
        {
            "trigger": ["hotkey", "up"],
            "type": "key",
            "target": ["KEY_F6"],
            "description": "Slot +",
        },
        {
            "trigger": ["hotkey", "left"],
            "type": "key",
            "target": ["KEY_F1"],
            "description": "Rewind",
        },
        {
            "trigger": ["hotkey", "right"],
            "type": "key",
            "target": ["KEY_F2"],
            "description": "Fast Forward",
        },
        {
            "trigger": ["hotkey", "pageup"],
            "type": "key",
            "target": ["KEY_F7"],
            "description": "Screenshot",
        },
        {
            "trigger": ["hotkey", "b"],
            "type": "key",
            "target": ["KEY_F9"],
            "description": "Pause / Menu",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for PSP.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
