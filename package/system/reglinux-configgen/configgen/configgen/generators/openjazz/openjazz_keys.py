"""Evmapy controller mappings for OPENJAZZ (OPENJAZZ).

This module defines button mappings for OPENJAZZ games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.openjazz import evmapy_openjazz
    config = evmapy_openjazz.get_config()

"""

from typing import Any

# Evmapy configuration for OPENJAZZ controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        }
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for OPENJAZZ.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
