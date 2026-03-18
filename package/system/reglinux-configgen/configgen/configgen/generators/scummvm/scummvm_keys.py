"""Evmapy controller mappings for SCUMMVM.

This module defines button mappings for SCUMMVM games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.scummvm import scummvm_keys
    config = scummvm_keys.get_config()

"""

from typing import Any

# Evmapy configuration for SCUMMVM controller
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
    """Return the evmapy configuration for SCUMMVM.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
