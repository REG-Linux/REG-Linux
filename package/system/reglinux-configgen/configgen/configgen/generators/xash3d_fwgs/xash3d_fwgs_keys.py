"""Evmapy controller mappings for XASH3D_FWGS (Half-Life engine).

This module defines button mappings for XASH3D_FWGS games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.xash3d_fwgs import xash3d_fwgs_keys
    config = xash3d_fwgs_keys.get_config()

"""

from typing import Any

# Evmapy configuration for XASH3D_FWGS controller
# This replaces the need for external .keys files
CONFIG: dict[str, Any] = {
    "actions_player1": [
        {
            "trigger": ["hotkey", "start"],
            "type": "key",
            "target": ["KEY_LEFTALT", "KEY_F4"],
        },
    ],
}


def get_config() -> dict[str, Any]:
    """Return the evmapy configuration for XASH3D_FWGS.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
