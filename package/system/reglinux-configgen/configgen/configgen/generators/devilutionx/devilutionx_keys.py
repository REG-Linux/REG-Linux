"""Evmapy controller mappings for DEVILUTIONX (DEVILUTIONX).

This module defines button mappings for DEVILUTIONX games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.devilutionx import evmapy_devilutionx
    config = evmapy_devilutionx.get_config()

"""

from typing import Any

# Evmapy configuration for DEVILUTIONX controller
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
    """Return the evmapy configuration for DEVILUTIONX.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
