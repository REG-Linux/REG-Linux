"""Evmapy controller mappings for VPINBALL (VPINBALL).

This module defines button mappings for VPINBALL games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.vpinball import evmapy_vpinball
    config = evmapy_vpinball.get_config()

"""

from typing import Any

# Evmapy configuration for VPINBALL controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_Q"],
            "description": "Exit the emulator",
        },
        {
            "trigger": ["hotkey", "a"],
            "type": "key",
            "target": ["KEY_F3"],
            "description": "Reset the table, sometimes required for PinMame",
        },
        {
            "trigger": ["start"],
            "type": "key",
            "target": ["KEY_1"],
            "description": "Start game",
        },
        {
            "trigger": ["select"],
            "type": "key",
            "target": ["KEY_5"],
            "description": "Insert coin",
        },
        {
            "trigger": ["up"],
            "type": "key",
            "target": ["KEY_SPACE"],
            "description": "Nudge up",
        },
        {
            "trigger": ["left"],
            "type": "key",
            "target": ["KEY_Z"],
            "description": "Nudge left",
        },
        {
            "trigger": ["right"],
            "type": "key",
            "target": ["KEY_SLASH"],
            "description": "Nudge right",
        },
        {
            "trigger": ["b"],
            "type": "key",
            "target": ["KEY_ENTER"],
            "description": "Pull plunger",
        },
        {
            "trigger": ["a"],
            "type": "key",
            "target": ["KEY_LEFTALT"],
            "description": "Lockbar Fire Button",
        },
        {
            "trigger": ["y"],
            "type": "key",
            "target": ["KEY_2"],
            "description": "Buy extraball for a credit",
        },
        {
            "trigger": ["pageup"],
            "type": "key",
            "target": ["KEY_LEFTSHIFT"],
            "description": "Left flipper",
        },
        {
            "trigger": ["pagedown"],
            "type": "key",
            "target": ["KEY_RIGHTSHIFT"],
            "description": "Right flipper",
        },
        {
            "trigger": ["l2"],
            "type": "key",
            "target": ["KEY_LEFTSHIFT"],
            "description": "Left flipper",
        },
        {
            "trigger": ["r2"],
            "type": "key",
            "target": ["KEY_RIGHTSHIFT"],
            "description": "Right flipper",
        },
        {
            "trigger": ["l3"],
            "type": "key",
            "target": ["KEY_LEFTCTRL"],
            "description": "Left magnasave",
        },
        {
            "trigger": ["r3"],
            "type": "key",
            "target": ["KEY_RIGHTCTRL"],
            "description": "Right magnasave",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for VPINBALL.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
