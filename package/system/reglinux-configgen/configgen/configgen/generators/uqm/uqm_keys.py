"""Evmapy controller mappings for UQM (UQM).

This module defines button mappings for UQM games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.uqm import evmapy_uqm
    config = evmapy_uqm.get_config()

"""

from typing import Any

# Evmapy configuration for UQM controller
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
    """Return the evmapy configuration for UQM.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
