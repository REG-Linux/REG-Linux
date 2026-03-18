#!/usr/bin/env python3
"""Emulator launcher for the RegLinux distribution.

DEPRECATED: This file is maintained for backward compatibility only.
New code should use configgen.launcher.emulator_launcher instead.

This module now delegates all functionality to the new launcher implementation.
"""

from argparse import ArgumentParser
from pathlib import Path
from signal import SIGINT, SIGTERM, signal
from time import sleep
from typing import Any

from configgen.config.paths import EMULATORLAUNCHER_PERF
from configgen.launcher import emulator_launcher
from configgen.launcher.emulator_launcher import launch_rom as new_launch_rom
from configgen.launcher.profiler import Profiler, is_profiling_enabled
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

# Profiling setup
_profiler_instance = Profiler(enabled=is_profiling_enabled())

# Enable cProfile if the performance marker file exists
if EMULATORLAUNCHER_PERF.exists():
    import cProfile

    _profiler_instance = cProfile.Profile()
    _profiler_instance.enable()

# Global alias for backward compatibility
profiler = _profiler_instance


def main(args: Any, maxnbplayers: int) -> int:
    """Entry point to start a ROM.

    DEPRECATED: This function now delegates to configgen.launcher.emulator_launcher.

    Args:
        args: Argument object containing at least `rom` (ROM file path).
        maxnbplayers: Maximum number of players supported for this game.

    Returns:
        Exit code from the ROM launcher.

    """
    return new_launch_rom(args, maxnbplayers)


if __name__ == "__main__":
    # Register signal handler for graceful termination.
    signal(SIGINT, emulator_launcher.signal_handler)
    signal(SIGTERM, emulator_launcher.signal_handler)

    # --- Argument Parsing ---
    parser = ArgumentParser(description="Emulator Launcher Script (DEPRECATED)")

    maxnbplayers = 8
    # Dynamically create arguments for each player's controller.
    for p in range(1, maxnbplayers + 1):
        parser.add_argument(
            f"-p{p}index",
            help=f"player {p} controller index",
            type=int,
        )
        parser.add_argument(
            f"-p{p}guid",
            help=f"player {p} controller SDL2 guid",
            type=str,
        )
        parser.add_argument(f"-p{p}name", help=f"player {p} controller name", type=str)
        parser.add_argument(
            f"-p{p}devicepath",
            help=f"player {p} controller device path",
            type=str,
        )
        parser.add_argument(
            f"-p{p}nbbuttons",
            help=f"player {p} controller number of buttons",
            type=str,
        )
        parser.add_argument(
            f"-p{p}nbhats",
            help=f"player {p} controller number of hats",
            type=str,
        )
        parser.add_argument(
            f"-p{p}nbaxes",
            help=f"player {p} controller number of axes",
            type=str,
        )

    # General arguments for system, ROM, and specific features.
    parser.add_argument(
        "-system",
        help="Select the system to launch",
        type=str,
        required=True,
    )
    parser.add_argument(
        "-rom",
        help="Absolute path to the ROM",
        type=str,
        required=True,
    )
    parser.add_argument("-emulator", help="Force a specific emulator", type=str)
    parser.add_argument("-core", help="Force a specific emulator core", type=str)
    parser.add_argument("-netplaymode", help="Netplay mode (host/client)", type=str)
    parser.add_argument("-netplaypass", help="Netplay spectator password", type=str)
    parser.add_argument("-netplayip", help="Netplay remote IP address", type=str)
    parser.add_argument("-netplayport", help="Netplay remote port", type=str)
    parser.add_argument("-netplaysession", help="Netplay session identifier", type=str)
    parser.add_argument("-state_slot", help="Load state from a specific slot", type=str)
    parser.add_argument(
        "-state_filename",
        help="Load state from a specific filename",
        type=str,
    )
    parser.add_argument("-autosave", help="Enable/disable autosave feature", type=str)
    parser.add_argument("-systemname", help="System's display name", type=str)
    parser.add_argument(
        "-gameinfoxml",
        help="Path to game info XML metadata",
        type=str,
        nargs="?",
        default="/dev/null",
    )
    parser.add_argument(
        "-lightgun",
        help="Configure for lightgun usage",
        action="store_true",
    )
    parser.add_argument("-wheel", help="Configure for wheel usage", action="store_true")

    args = parser.parse_args()
    exitcode = -1
    try:
        # Call the main function with parsed arguments.
        exitcode = main(args, maxnbplayers)
    except SystemExit:
        # Let system exit commands pass through (like sys.exit)
        raise
    except Exception as e:
        eslog.error(f"An unhandled exception occurred in configgen: {e}", exc_info=True)

    # If profiling was enabled, save the results.
    if profiler:
        try:
            if hasattr(profiler, "disable"):
                profiler.disable()  # pyright: ignore[reportAttributeAccessIssue]
            if hasattr(profiler, "dump_stats"):
                profiler.dump_stats(str(Path("/var/run/emulatorlauncher.prof")))  # pyright: ignore[reportAttributeAccessIssue]
        except Exception as e:
            eslog.error(f"Error dumping profiler stats: {e}")

    # A short delay can help ensure resources (like GPU memory) are fully released before returning to the frontend.
    sleep(1)
    eslog.debug(f"Exiting configgen with status {exitcode!s}")

    exit(exitcode)
