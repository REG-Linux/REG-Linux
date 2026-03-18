"""Evmapy controller mappings for SDLPOP (SDLPOP).

This module defines button mappings for SDLPOP games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.sdlpop import evmapy_sdlpop
    config = evmapy_sdlpop.get_config()

"""

from typing import Any

# Evmapy configuration for SDLPOP controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {"trigger": ["pageup"], "type": "key", "target": ["KEY_SPACE"]},
        {
            "trigger": ["hotkey", "a"],
            "type": "key",
            "target": ["KEY_LEFTCTRL", "KEY_R"],
        },
        {"trigger": ["hotkey", "y"], "type": "key", "target": ["KEY_F6"]},
        {"trigger": ["hotkey", "x"], "type": "key", "target": ["KEY_F9"]},
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTCTRL", "KEY_Q"],
        },
        {"trigger": ["hotkey", "pageup"], "type": "key", "target": ["KEY_F12"]},
        {
            "trigger": ["hotkey", "pagedown"],
            "type": "key",
            "target": ["KEY_LEFTCTRL", "KEY_A"],
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for SDLPOP.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
