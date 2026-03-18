"""Evmapy controller mappings for TARADINO (Quake engine).

This module defines button mappings for TARADINO games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.taradino import taradino_keys
    config = taradino_keys.get_config()

"""

from typing import Any

# Evmapy configuration for TARADINO controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
    ],
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for TARADINO.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
