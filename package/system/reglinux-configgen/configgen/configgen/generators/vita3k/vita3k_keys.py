"""Evmapy controller mappings for VITA3K (PSVITA).

This module defines button mappings for PSVITA games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.vita3k import evmapy_psvita
    config = evmapy_psvita.get_config()

"""

from typing import Any

# Evmapy configuration for PSVITA controller
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
    """Return the evmapy configuration for PSVITA.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
