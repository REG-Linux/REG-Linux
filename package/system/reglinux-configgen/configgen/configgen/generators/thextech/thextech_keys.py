"""Evmapy controller mappings for THEXTECH (THEXTECH).

This module defines button mappings for THEXTECH games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.thextech import evmapy_thextech
    config = evmapy_thextech.get_config()

"""

from typing import Any

# Evmapy configuration for THEXTECH controller
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
    """Return the evmapy configuration for THEXTECH.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
