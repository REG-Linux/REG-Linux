"""Evmapy controller mappings for ETLEGACY (ETLEGACY).

This module defines button mappings for ETLEGACY games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.etlegacy import evmapy_etlegacy
    config = evmapy_etlegacy.get_config()

"""

from typing import Any

# Evmapy configuration for ETLEGACY controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
            "description": "Exit game",
        }
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for ETLEGACY.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
