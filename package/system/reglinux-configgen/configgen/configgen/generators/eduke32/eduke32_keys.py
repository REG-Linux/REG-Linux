"""Evmapy controller mappings for EDUKE32 (EDUKE32).

This module defines button mappings for EDUKE32 games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.eduke32 import evmapy_eduke32
    config = evmapy_eduke32.get_config()

"""

from typing import Any

# Evmapy configuration for EDUKE32 controller
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
            "target": "KEY_F6",
            "description": "quicksave",
        },
        {
            "trigger": ["hotkey", "x"],
            "type": "key",
            "target": "KEY_F9",
            "description": "quickload",
        },
        {
            "trigger": ["hotkey", "pageup"],
            "type": "key",
            "target": "KEY_F12",
            "description": "screenshot",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for EDUKE32.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
