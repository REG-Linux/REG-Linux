"""Evmapy controller mappings for IORTCW (IORTCW).

This module defines button mappings for IORTCW games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.iortcw import evmapy_iortcw
    config = evmapy_iortcw.get_config()

"""

from typing import Any

# Evmapy configuration for IORTCW controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
        {
            "trigger": ["hotkey"],
            "type": "key",
            "target": ["KEY_ESC"],
            "description": "Skip cutscene",
        },
        {
            "trigger": ["hotkey", "y"],
            "type": "key",
            "target": "KEY_F5",
            "description": "Quick save",
        },
        {
            "trigger": ["hotkey", "x"],
            "type": "key",
            "target": "KEY_F9",
            "description": "Quick load",
        },
        {
            "trigger": ["hotkey", "pageup"],
            "type": "key",
            "target": "KEY_F11",
            "description": "Screenshot",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for IORTCW.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
