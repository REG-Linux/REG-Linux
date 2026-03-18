"""Evmapy controller mappings for SONIC2013.

This module defines button mappings for SONIC2013 games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.sonic2013 import sonic2013_keys
    config = sonic2013_keys.get_config()

"""

from typing import Any

# Evmapy configuration for SONIC2013 controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {"trigger": ["hotkey", "b"], "type": "key", "target": "KEY_ESC"},
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for SONIC2013.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
