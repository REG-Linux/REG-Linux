"""Evmapy controller mappings for ECWOLF (ECWOLF).

This module defines button mappings for ECWOLF games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.ecwolf import evmapy_ecwolf
    config = evmapy_ecwolf.get_config()

"""

from typing import Any

# Evmapy configuration for ECWOLF controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
        {"trigger": ["start"], "type": "key", "target": ["KEY_ESC"]},
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for ECWOLF.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
