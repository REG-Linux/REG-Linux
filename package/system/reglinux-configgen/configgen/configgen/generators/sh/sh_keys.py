"""Evmapy controller mappings for SH (Shell).

This module defines button mappings for SH games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.sh import sh_keys
    config = sh_keys.get_config()

"""

from typing import Any

# Evmapy configuration for SH controller
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
    """Return the evmapy configuration for SH.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
