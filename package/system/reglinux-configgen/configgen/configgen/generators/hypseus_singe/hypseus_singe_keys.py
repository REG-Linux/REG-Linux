"""Evmapy controller mappings for HYPSEUS.

This module defines button mappings for HYPSEUS SINGE and DAPHNE games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.hypseus_singe import hypseus_singe_keys
    config = hypseus_singe_keys.get_config("singe")

"""

from typing import Any

# Evmapy configuration for HYPSEUS controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_ESC"],
            "description": "Exit emulator",
        },
        {
            "trigger": ["hotkey", "b"],
            "type": "key",
            "target": ["KEY_9"],
            "description": "Service menu",
        },
    ],
    "actions_gun1": [
        {"trigger": "middle", "type": "key", "target": "KEY_5"},
        {"trigger": "1", "type": "key", "target": "KEY_1"},
    ],
    "actions_gun2": [
        {"trigger": "middle", "type": "key", "target": "KEY_6"},
        {"trigger": "1", "type": "key", "target": "KEY_2"},
    ],
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for HYPSEUS.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
