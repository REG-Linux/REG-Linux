"""Evmapy controller mappings for PCSX2 (PlayStation 2).

This module defines button mappings for PS2 games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.pcsx2 import evmapy_ps2
    config = evmapy_ps2.get_config()

"""

from typing import Any

# Evmapy configuration for PS2 controller
# This replaces the need for external .keys files
ACTIONS_PLAYER1: list[dict[str, Any]] = [
    # Hotkey combinations
    {
        "trigger": ["hotkey", "start"],
        "type": "key",
        "target": ["KEY_LEFTALT", "KEY_F4"],  # Save state
    },
    {
        "trigger": ["hotkey", "b"],
        "type": "key",
        "target": ["KEY_ESC"],  # Menu
    },
    {
        "trigger": ["hotkey", "x"],
        "type": "key",
        "target": ["KEY_F3"],  # Load state
    },
    {
        "trigger": ["hotkey", "y"],
        "type": "key",
        "target": ["KEY_F1"],  # Save state slot -
    },
    {
        "trigger": ["hotkey", "up"],
        "type": "key",
        "target": ["KEY_F2"],  # Save state slot +
    },
    {
        "trigger": ["hotkey", "down"],
        "type": "key",
        "target": ["KEY_LEFTSHIFT", "KEY_F2"],  # Save state slot --
    },
    {
        "trigger": ["hotkey", "pageup"],
        "type": "key",
        "target": ["KEY_F8"],  # Screenshot
    },
]

# Full configuration dictionary (compatible with .keys format)
CONFIG: dict[str, Any] = {
    "actions_player1": ACTIONS_PLAYER1,
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for PS2.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
