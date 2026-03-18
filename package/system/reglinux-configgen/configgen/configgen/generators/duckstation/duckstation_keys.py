"""Evmapy controller mappings for DUCKSTATION (PSX).

This module defines button mappings for PSX games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.duckstation import evmapy_psx
    config = evmapy_psx.get_config()

"""

from typing import Any

# Evmapy configuration for PSX controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
            "description": "Exit Duckstation",
        },
        {
            "trigger": ["hotkey", "x"],
            "type": "key",
            "target": ["KEY_F1"],
            "description": "Load State",
        },
        {
            "trigger": ["hotkey", "y"],
            "type": "key",
            "target": ["KEY_F2"],
            "description": "Save State",
        },
        {
            "trigger": ["hotkey", "b"],
            "type": "key",
            "target": ["KEY_F7"],
            "description": "Open DuckStation Quick Menu",
        },
        {
            "trigger": ["hotkey", "a"],
            "type": "key",
            "target": ["KEY_F6"],
            "description": "Restart Game",
        },
        {
            "trigger": ["hotkey", "pageup"],
            "type": "key",
            "target": ["KEY_F10"],
            "description": "Screenshot",
        },
        {
            "trigger": ["hotkey", "up"],
            "type": "key",
            "target": ["KEY_F3"],
            "description": "Slot -",
        },
        {
            "trigger": ["hotkey", "down"],
            "type": "key",
            "target": ["KEY_F4"],
            "description": "Slot +",
        },
        {
            "trigger": ["hotkey", "left"],
            "type": "key",
            "target": ["KEY_F5"],
            "description": "Rewind",
        },
        {
            "trigger": ["hotkey", "pagedown"],
            "type": "key",
            "target": ["KEY_F8"],
            "description": "Next Disc (m3u)",
        },
        {
            "trigger": ["hotkey", "right"],
            "type": "key",
            "target": ["KEY_TAB"],
            "description": "Fast Forward",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for PSX.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
