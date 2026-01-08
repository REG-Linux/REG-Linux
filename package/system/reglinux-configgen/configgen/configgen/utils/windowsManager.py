"""Window Manager Controller Module.

This module provides functionality to manage Wayland compositors (primarily Sway)
for gaming and application environments. It handles compositor lifecycle management
and proper environment variable configuration for both Wayland and X11 compatibility.
"""

from os import environ
from pathlib import Path
from subprocess import Popen, TimeoutExpired, run
from time import sleep
from typing import Any

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


class WindowManager:
    """Manages Wayland compositors (primarily Sway) using the Singleton pattern.

    This class centralizes the compositor lifecycle and state management.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # Initialize instance attributes
        self.sway_launched = False  # Tracks if Sway compositor is running
        self.sway_process: Popen | None = None  # Holds the Sway process reference
        self.gamescope_launched = False  # Reserved for future Gamescope implementation
        self._initialized = True

    def start_sway(self, generator: Any, system: Any) -> bool:
        """Start the Sway compositor and configure the environment for Wayland/X11.

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
                f"=======>> Sway process started with PID: {self.sway_process.pid}",
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
                },
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
                f"Sway process verification completed successfully after {attempt} attempts",
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
            eslog.error(f"Failed to start Sway: {e!s}")
            # Clean up if partial initialization occurred
            if self.sway_process and self.sway_process.poll() is None:
                self.sway_process.terminate()
            return False

    def stop_sway(self, generator: Any, system: Any) -> bool:
        """Gracefully stops the Sway compositor and cleans up the environment.

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
            # Send exit command to Sway - don't use check=True to avoid exception on non-zero exit
            result = run(["swaymsg", "exit"], timeout=5)

            # Check if the command executed but failed (non-zero exit code)
            if result.returncode != 0:
                eslog.warning(
                    f"swaymsg exit returned non-zero exit code: {result.returncode}"
                )
                # Continue with cleanup even if swaymsg failed, as Sway might have already terminated

            # Wait for process termination with a timeout
            if self.sway_process:
                try:
                    self.sway_process.wait(
                        timeout=2
                    )  # Shorter timeout for process termination
                except TimeoutExpired:
                    eslog.warning(
                        "Sway process did not terminate within timeout, attempting to kill"
                    )
                    try:
                        self.sway_process.kill()
                        self.sway_process.wait(
                            timeout=1
                        )  # Wait a bit more for the kill to complete
                    except Exception:
                        pass  # If we can't kill it, continue with cleanup
                finally:
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
            eslog.warning(
                "Swaymsg executable not found when trying to stop Sway, attempting to clean up process directly"
            )
            # Try to clean up the process directly if swaymsg is not available
            if self.sway_process:
                try:
                    self.sway_process.terminate()
                    self.sway_process.wait(timeout=2)
                except TimeoutExpired:
                    try:
                        self.sway_process.kill()
                        self.sway_process.wait(timeout=1)
                    except Exception:
                        pass  # If we can't kill it, continue with cleanup
                finally:
                    self.sway_process = None

            # Clean up environment variables even if swaymsg is not available
            for var in [
                "WAYLAND_DISPLAY",
                "XDG_RUNTIME_DIR",
                "SWAYSOCK",
                "SDL_VIDEODRIVER",
            ]:
                environ.pop(var, None)

            environ.update({"XDG_SESSION_TYPE": "drm", "QT_QPA_PLATFORM": "xcb"})

            if generator.requiresX11():
                environ.pop("DISPLAY", None)

            self.sway_launched = False
            return True
        except PermissionError:
            eslog.error("Permission denied when trying to stop Sway")
            return False
        except TimeoutExpired:
            eslog.warning(
                "Timeout while waiting for Sway to exit, attempting force kill"
            )
            # Force kill the process if it doesn't respond
            if self.sway_process:
                try:
                    self.sway_process.kill()
                    self.sway_process.wait(timeout=1)
                except Exception:
                    pass  # If we can't kill it, continue with cleanup
                finally:
                    self.sway_process = None

            # Still clean up environment variables
            for var in [
                "WAYLAND_DISPLAY",
                "XDG_RUNTIME_DIR",
                "SWAYSOCK",
                "SDL_VIDEODRIVER",
            ]:
                environ.pop(var, None)

            environ.update({"XDG_SESSION_TYPE": "drm", "QT_QPA_PLATFORM": "xcb"})

            if generator.requiresX11():
                environ.pop("DISPLAY", None)

            self.sway_launched = False
            return True
        except Exception as e:
            eslog.error(f"Error stopping Sway: {e!s}")
            # Perform cleanup even if there was an error
            if self.sway_process:
                try:
                    self.sway_process.kill()
                except Exception:
                    pass  # Ignore errors during force kill
                finally:
                    self.sway_process = None

            # Clean up environment variables
            for var in [
                "WAYLAND_DISPLAY",
                "XDG_RUNTIME_DIR",
                "SWAYSOCK",
                "SDL_VIDEODRIVER",
            ]:
                environ.pop(var, None)

            environ.update({"XDG_SESSION_TYPE": "drm", "QT_QPA_PLATFORM": "xcb"})

            if generator.requiresX11():
                environ.pop("DISPLAY", None)

            self.sway_launched = False
            return False


def start_compositor(generator: Any, system: Any) -> None:
    """Start the appropriate compositor based on system availability.

    Args:
        generator: Object that may specify display requirements
        system: System context object

    Raises:
        RuntimeError: If no supported compositor is found or fails to start

    """
    window_manager = WindowManager()

    if Path("/usr/bin/sway").exists():
        if not window_manager.start_sway(generator, system):
            raise RuntimeError(
                "Failed to start Sway compositor - check logs for details",
            )
        return

    # TODO: Implement Gamescope startup when available
    raise RuntimeError("No supported compositor found on this system")


def stop_compositor(generator: Any, system: Any) -> None:
    """Stop the currently running compositor.

    Args:
        generator: Object that may specify display requirements
        system: System context object

    Note:
        This function logs failures but does not raise exceptions to ensure
        emulator cleanup continues even if compositor stopping fails.

    """
    window_manager = WindowManager()

    if window_manager.sway_launched:
        if not window_manager.stop_sway(generator, system):
            eslog.warning(
                "Sway compositor did not stop cleanly, but continuing with cleanup",
            )
        return

    # TODO: Implement Gamescope shutdown when available
