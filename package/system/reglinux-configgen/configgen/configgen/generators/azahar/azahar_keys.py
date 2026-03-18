"""Evmapy controller mappings for AZAHAR (3DS).

This module defines button mappings for 3DS games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.azahar import evmapy_3ds
    config = evmapy_3ds.get_config()

"""

from typing import Any

# Evmapy configuration for 3DS controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {"trigger": "joystick2", "type": "mouse", "description": "Move Stylet Pointer"},
        {
            "trigger": "r3",
            "type": "key",
            "target": "BTN_LEFT",
            "description": "Mouse Click",
        },
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTCTRL", "KEY_Q"],
            "description": "Exit emulator",
        },
        {
            "trigger": ["hotkey", "a"],
            "type": "key",
            "target": "KEY_F6",
            "description": "Restart Emulation",
        },
        {
            "trigger": ["hotkey", "b"],
            "type": "key",
            "target": "KEY_F4",
            "description": "Continue/Pause emulation",
        },
        {
            "trigger": ["hotkey", "x"],
            "type": "key",
            "target": "KEY_F9",
            "description": "Swap Screen",
        },
        {
            "trigger": ["hotkey", "y"],
            "type": "key",
            "target": "KEY_F10",
            "description": "Toggle Screen Layout",
        },
        {
            "trigger": ["hotkey", "pageup"],
            "type": "key",
            "target": ["KEY_LEFTCTRL", "KEY_P"],
            "description": "Screenshot",
        },
        {
            "trigger": ["hotkey", "pagedown"],
            "type": "key",
            "target": ["KEY_LEFTCTRL", "KEY_Z"],
            "description": "Toggle Speed Limit",
        },
        {
            "trigger": ["hotkey", "r2"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_TAB"],
            "description": "Swap screens",
        },
    ]
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for 3DS.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
