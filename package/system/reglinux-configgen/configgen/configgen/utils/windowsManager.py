"""
Window Manager Controller Module

This module provides functionality to manage Wayland compositors (primarily Sway)
for gaming and application environments. It handles compositor lifecycle management
and proper environment variable configuration for both Wayland and X11 compatibility.
"""

from os import environ, path
from subprocess import Popen, TimeoutExpired, run
from time import sleep

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


class WindowManager:
    """
    Manages Wayland compositors (primarily Sway) using the Singleton pattern.
    This class centralizes the compositor lifecycle and state management.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WindowManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Initialize instance attributes
        self.sway_launched = False  # Tracks if Sway compositor is running
        self.sway_process: Popen | None = None  # Holds the Sway process reference
        self.gamescope_launched = False  # Reserved for future Gamescope implementation
        self._initialized = True

    def start_sway(self, generator, system) -> bool:
        """
        Starts the Sway compositor and configures the environment for Wayland/X11.

        Args:
            generator: An object that may specify X11 requirements (needs requiresX11() method)
            system: System context object (usage depends on implementation)

        Returns:
            bool: True if Sway started successfully, False otherwise

        Raises:
            SubprocessError: If the Sway process fails to start
        """

        if self.sway_launched:
            eslog.debug("Sway is already running")
            return True

        try:
            self.sway_process = Popen(
                ["/usr/bin/sway", "-c", "/etc/sway/launchconfig"],
                env={
                    **environ.copy(),
                    "WLR_LIBINPUT_NO_DEVICES": "1",  # Set as environment variable
                },
                start_new_session=True,
            )

            eslog.debug(
                "=======>> Sway process started with PID: %d", self.sway_process.pid
            )

            # Configure environment variables for Wayland compatibility
            environ.update(
                {
                    "WAYLAND_DISPLAY": "wayland-1",
                    "XDG_RUNTIME_DIR": "/var/run",
                    "SWAYSOCK": "/var/run/sway-ipc.0.sock",
                    "SDL_VIDEODRIVER": "wayland",
                    "XDG_SESSION_TYPE": "wayland",
                    "QT_QPA_PLATFORM": "wayland",
                }
            )

            # Handle X11 fallback if required by the generator
            if generator.requiresX11():
                environ.update({"DISPLAY": ":0", "QT_QPA_PLATFORM": "xcb"})

            # Verify process started successfully with retry mechanism
            max_attempts = 10  # Maximum number of attempts
            attempt = 0
            while attempt < max_attempts:
                if self.sway_process.poll() is not None:
                    eslog.error("Sway process terminated immediately after launch")
                    return False
                # Brief pause between checks
                sleep(0.3)
                attempt += 1

            # If we reach here, assume Sway is running
            eslog.debug(
                "Sway process verification completed successfully after %d attempts",
                attempt,
            )

            self.sway_launched = True
            eslog.info("Sway compositor started successfully")
            return True

        except FileNotFoundError:
            eslog.error("Sway executable not found at /usr/bin/sway")
            return False
        except PermissionError:
            eslog.error("Permission denied when trying to start Sway")
            return False
        except Exception as e:
            eslog.error(f"Failed to start Sway: {str(e)}")
            # Clean up if partial initialization occurred
            if self.sway_process and self.sway_process.poll() is None:
                self.sway_process.terminate()
            return False

    def stop_sway(self, generator, system) -> bool:
        """
        Gracefully stops the Sway compositor and cleans up the environment.

        Args:
            generator: The same generator object passed to start_sway()
            system: System context object

        Returns:
            bool: True if Sway stopped successfully, False otherwise
        """
        if not self.sway_launched:
            eslog.debug("Sway is not running")
            return True

        try:
            # Send exit command to Sway
            run(["swaymsg", "exit"], check=True, timeout=5)

            # Wait for process termination
            if self.sway_process:
                self.sway_process.wait(timeout=5)
                self.sway_process = None

            # Clean up environment variables
            for var in [
                "WAYLAND_DISPLAY",
                "XDG_RUNTIME_DIR",
                "SWAYSOCK",
                "SDL_VIDEODRIVER",
            ]:
                environ.pop(var, None)

            # Reset remaining environment settings
            environ.update({"XDG_SESSION_TYPE": "drm", "QT_QPA_PLATFORM": "xcb"})

            if generator.requiresX11():
                environ.pop("DISPLAY", None)

            self.sway_launched = False
            eslog.info("Sway compositor stopped successfully")
            return True

        except FileNotFoundError:
            eslog.error("Swaymsg executable not found when trying to stop Sway")
            return False
        except PermissionError:
            eslog.error("Permission denied when trying to stop Sway")
            return False
        except TimeoutExpired:
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
    window_manager = WindowManager()

    if path.exists("/usr/bin/sway"):
        if not window_manager.start_sway(generator, system):
            raise RuntimeError(
                "Failed to start Sway compositor - check logs for details"
            )
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
    window_manager = WindowManager()

    if window_manager.sway_launched:
        if not window_manager.stop_sway(generator, system):
            raise RuntimeError(
                "Failed to stop Sway compositor - check logs for details"
            )
        return

    # TODO: Implement Gamescope shutdown when available
