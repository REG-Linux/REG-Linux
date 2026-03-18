"""Evmapy controller mappings for Dosbox-X.

This module defines button mappings for Dosbox-X (DOS emulator) games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.dosboxx import dosboxx_keys
    config = dosboxx_keys.get_config()

"""

from typing import Any

# Evmapy configuration for Dosbox-X controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_ESC"],
            "description": "Exit Dosbox-X",
        },
        {
            "trigger": ["hotkey", "select"],
            "type": "key",
            "target": "KEY_F1",
            "description": "Dosbox-X menu",
        },
        {
            "trigger": ["hotkey", "pageup"],
            "type": "key",
            "target": "KEY_F9",
            "description": "Screenshot",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for Dosbox-X.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
