"""Evmapy controller mappings for ioquake3 (Quake III engine).

This module defines button mappings for ioquake3 games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.ioquake3 import ioquake3_keys
    config = ioquake3_keys.get_config()

"""

from typing import Any

# Evmapy configuration for ioquake3 controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": "up",
            "type": "key",
            "target": "KEY_UP",
        },
        {
            "trigger": "down",
            "type": "key",
            "target": "KEY_DOWN",
        },
        {
            "trigger": "left",
            "type": "key",
            "target": "KEY_LEFT",
        },
        {
            "trigger": "right",
            "type": "key",
            "target": "KEY_RIGHT",
        },
        {
            "trigger": "b",
            "type": "key",
            "target": "KEY_ENTER",
        },
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
        {
            "trigger": ["hotkey", "b"],
            "type": "key",
            "target": ["KEY_LEFTSHIFT", "KEY_ESC"],
        },
    ],
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for ioquake3.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
