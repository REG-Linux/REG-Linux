"""Evmapy controller mappings for OpenBOR.

This module defines button mappings for OpenBOR games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.openbor import openbor_keys
    config = openbor_keys.get_config()

"""

from typing import Any

# Evmapy configuration for OpenBOR controller
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
    """Return the evmapy configuration for OpenBOR.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
