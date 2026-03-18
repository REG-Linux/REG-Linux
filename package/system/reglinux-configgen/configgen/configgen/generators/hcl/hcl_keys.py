"""Evmapy controller mappings for HCL (HCL).

This module defines button mappings for HCL games using evmapy.
Mappings are loaded directly without file I/O for optimal performance.

Example:
    from configgen.generators.hcl import evmapy_hcl
    config = evmapy_hcl.get_config()

"""

from typing import Any

# Evmapy configuration for HCL controller
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
    """Return the evmapy configuration for HCL.

    Returns:
        Configuration dictionary compatible with evmapy format.

    """
    return CONFIG
