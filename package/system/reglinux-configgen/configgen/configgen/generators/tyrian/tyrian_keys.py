"""Evmapy controller mappings for TYRIAN (TYRIAN).

This module defines button mappings for TYRIAN games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.tyrian import evmapy_tyrian
    config = evmapy_tyrian.get_config()

"""

from typing import Any

# Evmapy configuration for TYRIAN controller
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
    """Return the evmapy configuration for TYRIAN.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
