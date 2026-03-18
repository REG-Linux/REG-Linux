"""Evmapy controller mappings for MELONDS (NDS).

This module defines button mappings for NDS games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.melonds import evmapy_nds
    config = evmapy_nds.get_config()

"""

from typing import Any

# Evmapy configuration for NDS controller
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
    """Return the evmapy configuration for NDS.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
