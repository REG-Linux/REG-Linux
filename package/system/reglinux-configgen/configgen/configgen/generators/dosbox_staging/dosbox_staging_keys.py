"""Evmapy controller mappings for Dosbox Staging.

This module defines button mappings for Dosbox Staging (DOS emulator) games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.dosbox_staging import dosbox_staging_keys
    config = dosbox_staging_keys.get_config()

"""

from typing import Any

# Evmapy configuration for Dosbox Staging controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_ESC"],
            "description": "Exit Dosbox Staging",
        },
        {
            "trigger": ["hotkey", "select"],
            "type": "key",
            "target": "KEY_F1",
            "description": "Dosbox Staging menu",
        },
        {
            "trigger": ["hotkey", "pageup"],
            "type": "key",
            "target": "KEY_F8",
            "description": "Screenshot",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for Dosbox Staging.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
