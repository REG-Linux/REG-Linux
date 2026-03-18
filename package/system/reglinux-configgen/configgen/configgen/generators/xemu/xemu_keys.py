"""Evmapy controller mappings for XEMU (XBOX).

This module defines button mappings for XBOX games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.xemu import evmapy_xbox
    config = evmapy_xbox.get_config()

"""

from typing import Any

# Evmapy configuration for XBOX controller
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
    """Return the evmapy configuration for XBOX.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
