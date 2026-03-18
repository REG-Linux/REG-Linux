"""Evmapy subpackage for REG-Linux ConfigGen.

This subpackage provides a native Python implementation for mapping
gamepad/controller inputs to keyboard/mouse events.

Acknowledgments:
    This implementation is based on the original evmapy project by kempniu.
    See: https://github.com/kempniu/evmapy

Features:
    - Zero file I/O: Configurations loaded directly from Python modules
    - Minimal latency: Optimized event loop with 1ms response time
    - Thread-safe: Uses threading.Event and threading.Lock for state management
    - Light gun support: Dedicated mouse button mapping for gun devices

Modules:
    event_handler: Core EvmapyNative class for event handling and uinput injection
    manager: High-level Evmapy manager for configuration loading and lifecycle

Example:
    from configgen.controllers.evmapy import Evmapy

    # Start evmapy with emulator configuration
    Evmapy.start(system, emulator, core, rom, players_controllers, guns)

    # ... emulator runs with controller mapping ...

    # Stop evmapy when done
    Evmapy.stop()

"""

from configgen.controllers.evmapy.event_handler import EvmapyNative
from configgen.controllers.evmapy.manager import Evmapy

__all__ = [
    "Evmapy",
    "EvmapyNative",
]
