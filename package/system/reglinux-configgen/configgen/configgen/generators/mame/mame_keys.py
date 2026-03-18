"""Evmapy controller mappings for MAME (MAME).

This module defines button mappings for MAME games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.mame import evmapy_mame
    config = evmapy_mame.get_config()

"""

from typing import Any

# Evmapy configuration for MAME controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {"trigger": ["hotkey", "start"], "type": "key", "target": ["KEY_ESC"]},
        {"trigger": ["hotkey", "b"], "type": "key", "target": ["KEY_TAB"]},
        {"trigger": ["hotkey", "x"], "type": "key", "target": ["KEY_F7"]},
        {
            "trigger": ["hotkey", "y"],
            "type": "key",
            "target": ["KEY_LEFTSHIFT", "KEY_F7"],
        },
        {"trigger": ["hotkey", "pageup"], "type": "key", "target": ["KEY_F12"]},
        {"trigger": ["hotkey", "right"], "type": "key", "target": ["KEY_PAGEDOWN"]},
        {"trigger": ["hotkey", "up"], "type": "key", "target": ["KEY_SCROLLLOCK"]},
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for MAME.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
