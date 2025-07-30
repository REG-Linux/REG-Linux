"""
Window Manager Controller Module

This module provides functionality to manage Wayland compositors (primarily Sway)
for gaming and application environments. It handles compositor lifecycle management
and proper environment variable configuration for both Wayland and X11 compatibility.
"""

import os
import subprocess
import time
from typing import Optional

from utils.logger import get_logger
eslog = get_logger(__name__)

# Global state tracking variables
sway_launched = False  # Tracks if Sway compositor is running
sway_process: Optional[subprocess.Popen] = None  # Holds the Sway process reference
gamescope_launched = False  # Reserved for future Gamescope implementation

def start_sway(generator, system) -> bool:
    """
    Starts the Sway compositor and configures the environment for Wayland/X11.

    Args:
        generator: An object that may specify X11 requirements (needs requiresX11() method)
        system: System context object (usage depends on implementation)

    Returns:
        bool: True if Sway started successfully, False otherwise

    Raises:
        subprocess.SubprocessError: If the Sway process fails to start
    """
    global sway_launched, sway_process

    if sway_launched:
        eslog.debug("Sway is already running")
        return True

    try:
        sway_process = subprocess.Popen(
            [
                "/usr/bin/sway",
                "-c", "/etc/sway/launchconfig"
            ],
            env={
                **os.environ.copy(),
                "WLR_LIBINPUT_NO_DEVICES": "1"  # Set as environment variable
            },
            start_new_session=True
        )

        eslog.debug("=======>> Sway process started with PID: %d", sway_process.pid)

        # Configure environment variables for Wayland compatibility
        os.environ.update({
            "WAYLAND_DISPLAY": "wayland-1",
            "XDG_RUNTIME_DIR": "/var/run",
            "SWAYSOCK": "/var/run/sway-ipc.0.sock",
            "SDL_VIDEODRIVER": "wayland",
            "XDG_SESSION_TYPE": "wayland",
            "QT_QPA_PLATFORM": "wayland"
        })

        # Handle X11 fallback if required by the generator
        if generator.requiresX11():
            os.environ.update({
                "DISPLAY": ":0",
                "QT_QPA_PLATFORM": "xcb"
            })

        # Verify process started successfully
        time.sleep(1)  # Brief pause to allow initialization
        if sway_process.poll() is not None:
            eslog.error("Sway process terminated immediately after launch")
            return False

        sway_launched = True
        eslog.info("Sway compositor started successfully")
        return True

    except Exception as e:
        eslog.error(f"Failed to start Sway: {str(e)}")
        # Clean up if partial initialization occurred
        if sway_process and sway_process.poll() is None:
            sway_process.terminate()
        return False

def stop_sway(generator, system) -> bool:
    """
    Gracefully stops the Sway compositor and cleans up the environment.

    Args:
        generator: The same generator object passed to start_sway()
        system: System context object

    Returns:
        bool: True if Sway stopped successfully, False otherwise
    """
    global sway_launched, sway_process

    if not sway_launched:
        eslog.debug("Sway is not running")
        return True

    try:
        # Send exit command to Sway
        subprocess.run(["swaymsg", "exit"], check=True, timeout=5)

        # Wait for process termination
        if sway_process:
            sway_process.wait(timeout=5)
            sway_process = None

        # Clean up environment variables
        for var in ["WAYLAND_DISPLAY", "XDG_RUNTIME_DIR", "SWAYSOCK", "SDL_VIDEODRIVER"]:
            os.environ.pop(var, None)

        # Reset remaining environment settings
        os.environ.update({
            "XDG_SESSION_TYPE": "drm",
            "QT_QPA_PLATFORM": "xcb"
        })

        if generator.requiresX11():
            os.environ.pop("DISPLAY", None)

        sway_launched = False
        eslog.info("Sway compositor stopped successfully")
        return True

    except subprocess.TimeoutExpired:
        eslog.error("Timeout while waiting for Sway to exit")
        return False
    except Exception as e:
        eslog.error(f"Error stopping Sway: {str(e)}")
        return False

def start_compositor(generator, system) -> None:
    """
    Starts the appropriate compositor based on system availability.

    Args:
        generator: Object that may specify display requirements
        system: System context object

    Raises:
        RuntimeError: If no supported compositor is found or fails to start
    """
    if os.path.exists("/usr/bin/sway"):
        if not start_sway(generator, system):
            raise RuntimeError("Failed to start Sway compositor - check logs for details")
        return

    # TODO: Implement Gamescope startup when available
    raise RuntimeError("No supported compositor found on this system")

def stop_compositor(generator, system) -> None:
    """
    Stops the currently running compositor.

    Args:
        generator: Object that may specify display requirements
        system: System context object

    Raises:
        RuntimeError: If compositor fails to stop properly
    """
    if sway_launched:
        if not stop_sway(generator, system):
            raise RuntimeError("Failed to stop Sway compositor - check logs for details")
        return

    # TODO: Implement Gamescope shutdown when available
