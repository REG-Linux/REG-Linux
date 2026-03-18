#!/usr/bin/env python3
"""Emulator launcher for the REG-Linux distribution.

This module is responsible for preparing the environment and launching the emulator
with the appropriate configurations.

This is the NEW implementation. The legacy emulatorlauncher.py delegates to this module.
"""

import json
import locale
import os
import signal
import tempfile
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from contextlib import suppress
from os import X_OK, access, chdir, environ
from os import path as osp
from pathlib import Path
from signal import SIGINT, SIGTERM
from subprocess import PIPE, CalledProcessError, Popen, TimeoutExpired, call
from threading import Lock, Thread
from typing import Any

from configgen import controllers
from configgen.archives import squashfs, zar
from configgen.bezel import bezel_base as bezelsUtil
from configgen.client import regmsg_connect
from configgen.config.paths import (
    HUD_CONFIG,
    SAVES,
)
from configgen.controllers import Evmapy
from configgen.controllers.utils import gunsUtils, wheelsUtils
from configgen.core import Emulator
from configgen.factory import getGenerator
from configgen.launcher.cleanup import CleanupManager, get_cleanup_manager
from configgen.launcher.hud_config import (
    hudConfig_protectStr,
)
from configgen.launcher.profiler import Profiler, is_profiling_enabled
from configgen.utils.logger import get_logger
from configgen.video import videoMode, windows_manager

eslog = get_logger(__name__)

# Enable the profiler if the performance marker file exists.
profiler = Profiler(enabled=is_profiling_enabled())

# Global process variable for signal handling with thread-safe access
_current_process: Popen | None = None
_process_lock = Lock()

# Sensitive keys that should be sanitized from logs
_SENSITIVE_KEYS = frozenset({
    "password",
    "pass",
    "secret",
    "token",
    "key",
    "credential",
})


def _sanitize_command(array: list[str]) -> list[str]:
    """Sanitize sensitive information from command arguments for logging.

    Args:
        array: List of command arguments.

    Returns:
        List with sensitive values replaced by '***'.

    """
    sanitized = []
    skip_next = False

    for arg in array:
        if skip_next:
            skip_next = False
            sanitized.append("***")  # Sanitize the value
            continue

        # Check if this argument is a sensitive key (with = or as separate arg)
        if "=" in arg:
            key, _, value = arg.partition("=")
            key_lower = key.lower()
            if any(sensitive in key_lower for sensitive in _SENSITIVE_KEYS):
                sanitized.append(f"{key}=***")
                continue
        elif arg.startswith("-"):
            arg_lower = arg.lower()
            if any(sensitive in arg_lower for sensitive in _SENSITIVE_KEYS):
                # Next argument is the value for this key
                skip_next = True
                sanitized.append(arg)
                continue

        sanitized.append(arg)

    return sanitized


def _set_current_process(proc: Popen | None) -> None:
    """Set the current emulator process for signal handling."""
    global _current_process
    with _process_lock:
        _current_process = proc


def _get_current_process() -> Popen | None:
    """Get the current emulator process."""
    with _process_lock:
        return _current_process


def signal_handler(signum: int, frame: Any) -> None:
    """Handle termination signals gracefully.

    Args:
        signum: The signal number.
        frame: The current stack frame.

    """
    eslog.info(f"Received signal {signum}, cleaning up...")

    proc = _get_current_process()
    if proc:
        try:
            # Send SIGINT to allow graceful shutdown
            proc.send_signal(signal.SIGINT)

            # Wait for process to terminate
            try:
                proc.wait(timeout=5)
            except TimeoutExpired:
                # Force kill if doesn't terminate
                proc.kill()
                proc.wait()
            except OSError as e:
                eslog.error(f"Error waiting for emulator process: {e}")

            eslog.info("Emulator process terminated")
        except (OSError, RuntimeError) as e:
            eslog.error(f"Error terminating emulator: {e}")

    # Cleanup resources
    cleanup = get_cleanup_manager()
    try:
        # Check if we're in an async context
        import asyncio

        try:
            asyncio.get_running_loop()
            # In async context, create a task
            asyncio.create_task(cleanup.cleanup_all())
        except RuntimeError:
            # No running loop, safe to use asyncio.run
            asyncio.run(cleanup.cleanup_all())
    except (RuntimeError, Exception) as e:
        eslog.error(f"Error during cleanup: {e}")

    # Exit
    os._exit(128 + signum)
    os._exit(0)


def launch_rom(args: Any, maxnbplayers: int) -> int:
    """Entry point to start a ROM, with optional mounting of .zar archive files.

    If the input ROM file is a .zar archive, this function mounts it,
    retrieves the actual ROM path, and launches the ROM.

    Args:
        args: Argument object containing at least `rom` (ROM file path).
        maxnbplayers: Maximum number of players supported for this game.

    Returns:
        Exit code from the ROM launcher.

    """
    # Connect ZeroMQ
    regmsg_connect()

    # Get the file extension in lowercase
    extension = Path(args.rom).suffix[1:].lower()

    # Check if it is a .zar or .squashfs archive
    need_end = False
    rommountpoint: str | None = None
    original_rom = args.rom

    if extension == "zar":
        try:
            need_end, rommountpoint, args.rom = zar.zar_begin(args.rom)
            eslog.info(f"Mounted .zar archive: {rommountpoint}")
        except Exception as e:
            eslog.error(f"Failed to mount .zar archive: {e}")
            return 1
    elif extension == "squashfs":
        try:
            need_end, rommountpoint, args.rom = squashfs.squashfs_begin(args.rom)
            eslog.info(f"Mounted .squashfs archive: {rommountpoint}")
        except Exception as e:
            eslog.error(f"Failed to mount .squashfs archive: {e}")
            return 1

    # Register with cleanup manager
    cleanup = get_cleanup_manager()
    if need_end and rommountpoint:
        cleanup.mark_rom_mounted(need_end, rommountpoint)

    # Start the ROM
    exit_code = start_rom(args, maxnbplayers, original_rom)

    # Cleanup archive if mounted
    if need_end and rommountpoint:
        try:
            if extension == "zar":
                zar.zar_end(rommountpoint)
            elif extension == "squashfs":
                squashfs.squashfs_end(rommountpoint)
        except Exception as e:
            eslog.error(f"Error unmounting archive: {e}")

    return exit_code


def start_rom(args: Any, maxnbplayers: int, original_rom: str | None = None) -> int:
    """Start the ROM with the appropriate emulator.

    Args:
        args: Argument object with ROM path and options.
        maxnbplayers: Maximum number of players supported.
        original_rom: Original ROM path (before archive mounting).

    Returns:
        Exit code from the emulator.

    """
    # Start profiling
    profiler.start()

    # Register signal handlers
    from signal import signal as signal_func

    signal_func(SIGINT, signal_handler)
    signal_func(SIGTERM, signal_handler)

    try:
        # Load emulator configuration
        system = Emulator(args.system, args.rom)
        eslog.info(
            f"System: {system.name}, Emulator: {system.config['emulator']}, Core: {system.config['core']}"
        )

        # Get generator for this emulator
        generator = getGenerator(system.config["emulator"])

        # Setup cleanup manager
        cleanup = get_cleanup_manager()

        # Configure controllers
        players_controllers = _configure_controllers(system, maxnbplayers, args)

        # Configure special devices (guns, wheels)
        metadata = _get_metadata(system, args.rom, args.gameinfoxml)
        guns, wheels, wheel_processes = _configure_special_devices(
            system, args, metadata, players_controllers
        )

        # Setup video and mouse
        system_mode, resolution_changed, mouse_changed, game_resolution = (
            _setup_video_and_mouse(system, generator, args.rom)
        )

        # Apply command-line options
        _apply_commandline_options(args, system)

        # Setup environment variables
        _setup_environment_variables(system)

        # Create save directory
        _create_save_directory(system)

        # Execute pre-launch scripts
        _execute_external_scripts(system, args.rom, "gameStart")

        # Configure HUD and bezels
        _configure_hud(system, generator, args.rom, metadata, game_resolution, guns)

        # Setup evmapy and compositor if needed
        evmapy_thread = _setup_evmapy_and_compositor(
            generator, system, args, players_controllers, guns
        )

        # Prepare and execute emulator command
        command = _prepare_emulator_command(
            generator,
            system,
            args.rom,
            players_controllers,
            metadata,
            guns,
            wheels,
            game_resolution,
        )

        # Run emulator with profiler
        exit_code = _run_emulator_with_profiler(command, cleanup)

        # Execute post-launch scripts
        _execute_external_scripts(system, args.rom, "gameStop")

        # Cleanup evmapy
        if evmapy_thread and evmapy_thread.is_alive():
            evmapy_thread.join(timeout=5)

        # Cleanup system resources
        _cleanup_system(resolution_changed, system_mode, mouse_changed, wheel_processes)

        return exit_code

    except Exception as e:
        eslog.error(f"Error starting ROM: {e}", exc_info=True)
        return 1
    finally:
        # Stop profiling
        profiler.stop()


# Module-level constant for controller attribute names
_CONTROLLER_ATTRS = (
    "index",
    "guid",
    "name",
    "devicepath",
    "nbbuttons",
    "nbhats",
    "nbaxes",
)


def _configure_controllers(
    system: Emulator,
    maxnbplayers: int,
    args: Any,
) -> dict[str, Any]:
    """Configure controllers for the game.

    Args:
        system: The emulator configuration.
        maxnbplayers: Maximum number of players.
        args: Command-line arguments.

    Returns:
        Dictionary of player controller configurations.

    """
    # Build controller input from command-line arguments
    controllers_input: list[dict[str, Any]] = []

    for p in range(1, maxnbplayers + 1):
        ci = {attr: getattr(args, f"p{p}{attr}", None) for attr in _CONTROLLER_ATTRS}
        controllers_input.append(ci)

    # Load controller configuration
    players_controllers = controllers.load_controller_config(controllers_input)

    eslog.debug(f"Controllers configured for {len(players_controllers)} players")
    return players_controllers


def _start_evmapy_async(
    system: Emulator,
    emulator: str,
    core: str,
    rom: str,
    players_controllers: Any,
    guns: Any,
) -> Thread:
    """Start Evmapy asynchronously in a background thread.

    This prevents the emulator startup from being delayed by Evmapy initialization.
    Evmapy will run in parallel while the emulator is already loading.

    Args:
        system: The system identifier (e.g., "nes", "snes").
        emulator: The emulator name.
        core: The emulator core name.
        rom: Path used for specific ROM configuration.
        players_controllers: Controller configuration for all players.
        guns: Configured light guns (if any).

    Returns:
        threading.Thread: The thread running Evmapy.

    """

    def worker():
        try:
            Evmapy.start(system, emulator, core, rom, players_controllers, guns)
        except Exception as e:
            eslog.error(f"Evmapy failed: {e}", exc_info=True)

    # Start the Evmapy worker in background mode (daemon thread).
    t = Thread(target=worker, daemon=True)
    t.start()
    return t


def _get_metadata(system: Emulator, rom: str, gameinfoxml: str) -> dict[str, Any]:
    """Get game metadata.

    Args:
        system: The emulator configuration.
        rom: Path to the ROM file.
        gameinfoxml: Path to game info XML metadata.

    Returns:
        Dictionary of game metadata.

    """
    metadata: dict[str, Any] = {}

    # Load metadata from EmulationStation
    try:
        metadata = controllers.getGamesMetaData(system.name, rom)
    except Exception as e:
        eslog.warning(f"Failed to load metadata: {e}")

    return metadata


def _configure_special_devices(
    system: Emulator,
    args: Any,
    metadata: dict[str, Any],
    players_controllers: dict[str, Any],
) -> tuple[dict[str, Any] | list[Any], dict[str, Any] | list[Any], list[Any]]:
    """Configure light guns and racing wheels.

    Args:
        system: The emulator configuration.
        args: Command-line arguments.
        metadata: Game metadata.
        players_controllers: Player controller configurations.

    Returns:
        Tuple of (guns, wheels, wheel_processes) lists.

    """
    # Configure guns
    guns: dict[str, Any] | list[Any] = []
    if not system.isOptSet("use_guns") and args.lightgun:
        system.config["use_guns"] = True
    if system.isOptSet("use_guns") and system.getOptBoolean("use_guns"):
        guns = controllers.getGuns()
        core = system.config.get("core", "")
        gunsUtils.precalibration(
            system.name, system.config["emulator"], core or "", system.rom
        )
    else:
        eslog.info("Guns disabled.")

    # Configure wheels
    wheels: dict[str, Any] | list[Any] = []
    wheel_processes: list[Any] = []

    if not system.isOptSet("use_wheels") and args.wheel:
        system.config["use_wheels"] = True
    if system.isOptSet("use_wheels") and system.getOptBoolean("use_wheels"):
        device_infos = controllers.getDevicesInformation()
        (wheel_processes, players_controllers, device_infos) = (
            wheelsUtils.reconfigure_controllers(
                players_controllers,
                system,
                system.rom,
                metadata,
            )
        )
        wheels = wheelsUtils.get_wheels_from_device_infos(device_infos)
    else:
        eslog.info("Wheels disabled.")

    return guns, wheels, wheel_processes


def _setup_video_and_mouse(
    system: Emulator,
    generator: Any,
    rom: str,
) -> tuple[Any, bool, bool, dict[str, int]]:
    """Set up video mode and mouse visibility for the game.

    Args:
        system: The emulator configuration.
        generator: The emulator generator.
        rom: Path to the ROM file.

    Returns:
        Tuple of (system_mode, resolution_changed, mouse_changed, game_resolution).

    """
    wanted_game_mode = generator.getResolutionMode(system.config)
    system_mode = videoMode.getCurrentMode()
    resolution_changed = False
    mouse_changed = False

    new_system_mode = system_mode
    if system.config.get("videomode", "default") in ["", "default"]:
        eslog.debug("==== minTomaxResolution ====")
        eslog.debug(f"Video mode before minmax: {system_mode}")
        videoMode.minTomaxResolution()
        new_system_mode = videoMode.getCurrentMode()
        if new_system_mode != system_mode:
            resolution_changed = True

    eslog.debug(f"Current video mode: {new_system_mode}")
    eslog.debug(f"Wanted video mode: {wanted_game_mode}")

    if wanted_game_mode != "default" and wanted_game_mode != new_system_mode:
        videoMode.changeMode(wanted_game_mode)
        resolution_changed = True
    game_resolution = videoMode.getCurrentResolution()

    if generator.getMouseMode(system.config, rom):
        mouse_changed = True
        videoMode.changeMouse(True)

    return system_mode, resolution_changed, mouse_changed, game_resolution


def _apply_commandline_options(args: Any, system: Emulator) -> None:
    """Apply command-line options to the system configuration.

    Args:
        args: Command-line arguments.
        system: The emulator configuration.

    """
    if args.netplaymode is not None:
        system.config["netplay.mode"] = args.netplaymode
    if args.netplaypass is not None:
        system.config["netplay.password"] = args.netplaypass
    if args.netplayip is not None:
        system.config["netplay.server.ip"] = args.netplayip
    if args.netplayport is not None:
        system.config["netplay.server.port"] = args.netplayport
    if args.netplaysession is not None:
        system.config["netplay.server.session"] = args.netplaysession

    if args.state_slot is not None:
        system.config["state_slot"] = args.state_slot
    if args.autosave is not None:
        system.config["autosave"] = args.autosave
    if args.state_filename is not None:
        system.config["state_filename"] = args.state_filename


def _setup_environment_variables(system: Emulator) -> None:
    """Set up environment variables for the emulator.

    Args:
        system: The emulator configuration.

    """
    system.config["sdlvsync"] = (
        "0"
        if system.isOptSet("sdlvsync") and not system.getOptBoolean("sdlvsync")
        else "1"
    )
    environ["SDL_RENDER_VSYNC"] = system.config["sdlvsync"]

    # Set keyboard and locale environment variables to prevent xkbcommon errors
    # Use UTF-8 locale to ensure Qt compatibility
    try:
        locale.setlocale(locale.LC_ALL, "C.UTF-8")
        environ["LC_ALL"] = "C.UTF-8"
        environ["LANG"] = "C.UTF-8"
        environ["LANGUAGE"] = "C.UTF-8"
        environ["LC_CTYPE"] = "C.UTF-8"
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
            environ["LC_ALL"] = "en_US.UTF-8"
            environ["LANG"] = "en_US.UTF-8"
            environ["LANGUAGE"] = "en_US.UTF-8"
            environ["LC_CTYPE"] = "en_US.UTF-8"
        except locale.Error:
            environ["LC_ALL"] = "C"
            environ["LANG"] = "C"
            environ["LANGUAGE"] = "C"
            environ["LC_CTYPE"] = "C"
            eslog.warning(
                "UTF-8 locales not available, falling back to 'C' locale. This may cause issues with Qt applications.",
            )

    # Set XKB configuration to prevent compose file errors
    environ["XKB_DEFAULT_OPTIONS"] = ""
    environ["XKB_LOG_LEVEL"] = "critical"


def _execute_external_scripts(system: Emulator, rom: str, event: str) -> None:
    """Execute external scripts based on the event type.

    Args:
        system: The emulator configuration.
        rom: Path to the ROM file.
        event: The event type (e.g., "gameStart", "gameStop").

    """
    effectiveCore = system.config.get("core", "")
    effectiveRom = rom or ""

    script_directories = [
        Path("/usr/share/reglinux/configgen/scripts"),
        Path("/userdata/system/scripts"),
    ]

    # For gameStart events, we want the first directory to be user scripts
    if event == "gameStop":
        script_directories.reverse()

    for directory in script_directories:
        callExternalScripts(
            str(directory),
            event,
            [system.name, system.config["emulator"], effectiveCore, effectiveRom],
        )


def _create_save_directory(system: Emulator) -> None:
    """Create the save directory for the system if it doesn't exist.

    Args:
        system: The emulator configuration.

    """
    dirname = SAVES / system.name
    dirname.mkdir(exist_ok=True, parents=True)


def _cleanup_hud_config() -> None:
    """Clean up the temporary HUD config file."""
    try:
        try:
            HUD_CONFIG.unlink()
        except FileNotFoundError:
            pass
        except Exception as e:
            eslog.warning(f"Could not remove HUD config file: {e}")
    except Exception as e:
        eslog.warning(f"Error processing HUD config file: {e}")


def _cleanup_temp_files(*temp_files: str) -> None:
    """Clean up temporary files created during bezel processing.

    Args:
        *temp_files: Variable number of temporary file paths to cleanup.

    """
    for temp_file in temp_files:
        try:
            if temp_file:
                try:
                    Path(temp_file).unlink()
                except FileNotFoundError:
                    pass
                except Exception as e:
                    eslog.warning(f"Could not remove temporary file {temp_file}: {e}")
        except Exception as e:
            eslog.warning(f"Error processing temporary file {temp_file}: {e}")


def getHudBezel(
    system: Emulator,
    generator: Any,
    rom: str,
    game_resolution: dict[str, int],
    borders_size: Any,
) -> str | None:
    """Determine and prepare the appropriate bezel image for the HUD.

    It checks for bezel compatibility (aspect ratio, coverage) and resizes,
    tattoos, or adds borders to the image as needed.

    Args:
        system: The current system's configuration object.
        generator: The emulator-specific generator.
        rom: Path to the ROM file.
        game_resolution: The current game resolution.
        borders_size: The size of the gun borders, if any.

    Returns:
        The path to the final bezel image file, or None if no bezel should be used.

    """
    # Skip if the emulator handles its own bezels.
    if generator.supportsInternalBezels():
        eslog.debug(f"Skipping bezels for emulator {system.config['emulator']}")
        return None

    # Skip if no bezel is configured and no special effects (tattoo, borders) are needed.
    if (
        ("bezel" not in system.config or system.config["bezel"] in ["", "none"])
        and not (
            system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0"
        )
        and borders_size is None
    ):
        return None

    # List of temporary files that may be created
    temp_files: list[str] = []

    try:
        # If no bezel is set but effects are needed, create a transparent base.
        if "bezel" not in system.config or system.config["bezel"] in ["", "none"]:
            with tempfile.NamedTemporaryFile(
                suffix=".png",
                prefix="bezel_transhud_",
                delete=False,
            ) as png_temp:
                overlay_png_file = png_temp.name
            with tempfile.NamedTemporaryFile(
                suffix=".info",
                prefix="bezel_transhud_",
                delete=False,
            ) as info_temp:
                overlay_info_file = info_temp.name

            temp_files.extend([overlay_png_file, overlay_info_file])
            bezelsUtil.createTransparentBezel(
                overlay_png_file,
                game_resolution["width"],
                game_resolution["height"],
            )

            w, h = game_resolution["width"], game_resolution["height"]
            Path(overlay_info_file).write_text(
                f'{{"width":{w}, "height":{h}, "opacity":1.0, "messagex":0.22, "messagey":0.12}}'
            )
        else:
            # A bezel is configured, so let's find its files.
            eslog.debug(
                f"HUD enabled. Trying to apply the bezel {system.config['bezel']}"
            )
            bezel = system.config["bezel"]
            bz_infos = bezelsUtil.getBezelInfos(
                rom,
                bezel,
                system.name,
                system.config["emulator"],
            )
            if bz_infos is None:
                eslog.debug("No bezel info file found")
                return None
            overlay_info_file = bz_infos["info"]
            overlay_png_file = bz_infos["png"]

            # Ensure types are correct (filter out bool/None values)
            if not isinstance(overlay_info_file, str) or not isinstance(
                overlay_png_file, str
            ):
                eslog.warning(
                    f"Invalid bezel info types: info={type(overlay_info_file)}, png={type(overlay_png_file)}"
                )
                return None

        # --- Bezel Validation ---
        infos = {}
        try:
            if overlay_info_file and isinstance(overlay_info_file, str):
                with Path(overlay_info_file).open() as f:
                    infos = json.load(f)
            else:
                eslog.warning(f"Invalid overlay info file: {overlay_info_file}")
        except FileNotFoundError:
            eslog.warning(f"Bezel info file not found: {overlay_info_file}")
        except json.JSONDecodeError as e:
            eslog.warning(f"Invalid JSON in bezel info file {overlay_info_file}: {e}")
        except Exception as e:
            eslog.warning(f"Unable to read bezel info file {overlay_info_file}: {e}")

        # Get bezel dimensions either from info file or the image itself.
        if "width" in infos and "height" in infos:
            bezel_width: int = infos["width"]
            bezel_height: int = infos["height"]
        elif overlay_png_file and isinstance(overlay_png_file, str):
            bezel_width, bezel_height = bezelsUtil.fast_image_size(overlay_png_file)
        else:
            eslog.error(f"Invalid overlay PNG file: {overlay_png_file}")
            return None

        eslog.debug(f"Bezel dimensions: {bezel_width}x{bezel_height}")

        # Define validation thresholds.
        max_ratio_delta = 0.01
        # Prevent division by zero if resolution detection failed
        if game_resolution["height"] == 0:
            eslog.warning("Invalid game resolution height, using default 16:9 ratio")
            screen_ratio: float = 16 / 9
        else:
            screen_ratio: float = game_resolution["width"] / game_resolution["height"]
        bezel_ratio: float = bezel_width / bezel_height

        # Validate aspect ratio (unless gun borders are being added).
        if borders_size is None and abs(screen_ratio - bezel_ratio) > max_ratio_delta:
            eslog.debug(
                f"Screen ratio ({screen_ratio}) is too far from the bezel one ({bezel_ratio})"
            )
            return None

        # --- Bezel Processing ---
        with ThreadPoolExecutor(max_workers=1) as executor:
            # Resize the bezel image if it doesn't match the screen resolution.
            bezel_stretch = system.isOptSet("bezel_stretch") and system.getOptBoolean(
                "bezel_stretch"
            )
            if (
                bezel_width != game_resolution["width"]
                or bezel_height != game_resolution["height"]
            ):
                eslog.debug("Bezel needs to be resized")
                with tempfile.NamedTemporaryFile(
                    suffix=".png",
                    prefix="bezel_resize_",
                    delete=False,
                ) as temp_file:
                    output_png_file = temp_file.name
                temp_files.append(output_png_file)
                if overlay_png_file and isinstance(overlay_png_file, (str, Path)):
                    try:
                        future = executor.submit(
                            bezelsUtil.resizeImage,
                            str(overlay_png_file),
                            output_png_file,
                            game_resolution["width"],
                            game_resolution["height"],
                            bezel_stretch,
                        )
                        future.result()
                        overlay_png_file = output_png_file
                    except Exception as e:
                        eslog.error(f"Failed to resize the image: {e}")
                        return None
                else:
                    eslog.error(
                        f"Invalid overlay PNG file for resize: {overlay_png_file}"
                    )
                    return None

            # Apply a "tattoo" (watermark/logo) to the bezel if configured.
            if system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0":
                with tempfile.NamedTemporaryFile(
                    suffix=".png",
                    prefix="bezel_tattooed_",
                    delete=False,
                ) as temp_file:
                    output_png_file = temp_file.name
                temp_files.append(output_png_file)
                if overlay_png_file and isinstance(overlay_png_file, (str, Path)):
                    future = executor.submit(
                        bezelsUtil.tatooImage,
                        str(overlay_png_file),
                        output_png_file,
                        system,
                    )
                    future.result()
                    overlay_png_file = output_png_file
                else:
                    eslog.error(
                        f"Invalid overlay PNG file for tattoo: {overlay_png_file}"
                    )
                    return None

            # Draw gun borders on the bezel if required.
            if borders_size is not None:
                eslog.debug("Drawing gun borders")
                with tempfile.NamedTemporaryFile(
                    suffix=".png",
                    prefix="bezel_gunborders_",
                    delete=False,
                ) as temp_file:
                    output_png_file = temp_file.name
                temp_files.append(output_png_file)
                inner_size, outer_size = bezelsUtil.gun_borders_size(borders_size)
                color = bezelsUtil.gunsBordersColorFomConfig(system.config)
                if overlay_png_file and isinstance(overlay_png_file, (str, Path)):
                    future = executor.submit(
                        bezelsUtil.gunBorderImage,
                        str(overlay_png_file),
                        output_png_file,
                        inner_size,
                        outer_size,
                        color,
                    )
                    future.result()
                    overlay_png_file = output_png_file
                else:
                    eslog.error(
                        f"Invalid overlay PNG file for gun border: {overlay_png_file}"
                    )
                    return None

        eslog.debug(f"Applying bezel {overlay_png_file}")
        return overlay_png_file

    finally:
        # Clean up temporary files
        _cleanup_temp_files(*temp_files)


def extractGameInfosFromXml(xml: str) -> dict[str, Any]:
    """Parse a game information XML file to extract game name and thumbnail.

    Args:
        xml: Path to the game info XML file.

    Returns:
        A dictionary containing 'name' and 'thumbnail' if found.

    """
    vals: dict[str, Any] = {}

    # Skip parsing if xml is /dev/null or empty path
    if not xml or xml == "/dev/null":
        return vals

    try:
        infos = ET.parse(xml)
        name_elem = infos.find("./game/name")
        if name_elem is not None and name_elem.text:
            vals["name"] = name_elem.text.strip()
        thumbnail_elem = infos.find("./game/thumbnail")
        if thumbnail_elem is not None and thumbnail_elem.text:
            vals["thumbnail"] = thumbnail_elem.text.strip()
    except ET.ParseError as e:
        eslog.warning(f"Failed to parse XML file {xml}: {e}")
    except FileNotFoundError as e:
        eslog.warning(f"XML file not found {xml}: {e}")
    except Exception as e:
        eslog.warning(f"Unexpected error parsing XML file {xml}: {e}")
    return vals


def callExternalScripts(folder: str, event: str, args: list[str]) -> None:
    """Execute all executable scripts in a given folder.

    Args:
        folder: The directory containing the scripts.
        event: The event name (e.g., "gameStart", "gameStop").
        args: A list of arguments to pass to the scripts.

    """
    # Sanitize the folder path to prevent directory traversal
    folder = osp.normpath(folder)
    if not Path(folder).is_dir():
        return

    # Only allow execution from known safe directories
    safe_paths = [
        "/usr/share/reglinux/configgen/scripts",
        "/userdata/system/scripts",
    ]
    if not any(folder.startswith(safe_path) for safe_path in safe_paths):
        eslog.warning(f"Script execution not allowed from unsafe directory: {folder}")
        return

    try:
        file_list = sorted(os.listdir(folder))
    except OSError as e:
        eslog.warning(f"Could not read directory {folder}: {e}")
        return

    for file in file_list:
        filepath = osp.normpath(osp.join(folder, file))

        # Additional check to ensure the file is within the allowed directory
        if not filepath.startswith(folder):
            eslog.warning(f"Unsafe file path detected: {filepath}")
            continue

        if Path(filepath).is_dir():
            callExternalScripts(
                filepath,
                event,
                args,
            )  # Recurse into subdirectories.
        elif access(filepath, X_OK):
            _, ext = osp.splitext(filepath)
            if ext.lower() in [".sh", ".py", ".pl", ".rb", ""]:
                script_args = [filepath, event] + args
                with suppress(BrokenPipeError):
                    eslog.debug(f"Calling external script: {script_args!s}")
                try:
                    result = call(script_args)
                    if result != 0:
                        with suppress(BrokenPipeError):
                            eslog.warning(
                                f"External script {filepath} returned non-zero exit code: {result}"
                            )
                except OSError as e:
                    with suppress(BrokenPipeError):
                        eslog.error(
                            f"Failed to execute external script {filepath}: {e}"
                        )
                except Exception as e:
                    with suppress(BrokenPipeError):
                        eslog.error(
                            f"Unexpected error executing external script {filepath}: {e}"
                        )
            else:
                eslog.warning(f"Skipping script with unsafe extension: {filepath}")


def _configure_hud(
    system: Emulator,
    generator: Any,
    rom: str,
    metadata: dict[str, Any],
    game_resolution: dict[str, int],
    guns: dict[str, Any] | list[Any],
) -> None:
    """Configure and enable MangoHUD if supported.

    Args:
        system: The emulator configuration.
        generator: The emulator generator.
        rom: Path to the ROM file.
        metadata: Game metadata.
        game_resolution: Current game resolution.
        guns: Configured light guns.

    """
    # Early exit if HUD not supported or not enabled
    if not system.isOptSet("hud_support") or not system.getOptBoolean("hud_support"):
        return

    # Early exit if MangoHUD not installed
    if not Path("/usr/bin/mangohud").exists():
        return

    # Check if HUD is explicitly enabled
    hud_enabled = system.isOptSet("hud") and system.config["hud"] not in ["", "none"]

    # Early exit if HUD not enabled (skip expensive bezel processing)
    if not hud_enabled:
        return

    hud_bezel = getHudBezel(
        system,
        generator,
        rom,
        game_resolution,
        controllers.guns_borders_size_name(
            guns if isinstance(guns, dict) else {}, system.config
        ),
    )

    if hud_bezel is not None:
        gameinfos = extractGameInfosFromXml("/dev/null")
        effective_core = system.config.get("core", "")
        hudconfig = getHudConfig(
            system,
            system.name,
            system.config["emulator"],
            effective_core,
            rom,
            gameinfos,
            hud_bezel,
        )

        HUD_CONFIG.write_text(hudconfig)
        # Note: HUD config application to command happens in _prepare_emulator_command


def _setup_evmapy_and_compositor(
    generator: Any,
    system: Emulator,
    args: Any,
    players_controllers: dict[str, Any],
    guns: dict[str, Any] | list[Any],
) -> Thread | None:
    """Set up Evmapy and compositor before launching the emulator.

    Args:
        generator: Emulator-specific generator instance.
        system: System configuration object.
        args: Command-line arguments.
        players_controllers: Controller configuration for all players.
        guns: Configured light guns (if any).

    Returns:
        threading.Thread: The thread running Evmapy, or None.

    """
    # Start Evmapy in a separate thread (non-blocking)
    evmapy_thread = _start_evmapy_async(
        system,
        system.config["emulator"],
        system.config.get("core", ""),
        system.rom,
        players_controllers,
        guns,
    )

    # Start a compositor if required (Wayland or X11)
    if (
        generator.requiresWayland() or generator.requiresX11()
    ) and "WAYLAND_DISPLAY" not in environ:
        windows_manager.start_compositor(generator, system)

    return evmapy_thread


def _prepare_emulator_command(
    generator: Any,
    system: Emulator,
    rom: str,
    players_controllers: dict[str, Any],
    metadata: dict[str, Any],
    guns: dict[str, Any] | list[Any],
    wheels: dict[str, Any] | list[Any],
    game_resolution: dict[str, int],
) -> Any:
    """Prepare the emulator command with all necessary configurations.

    Args:
        generator: Emulator-specific generator instance.
        system: System configuration object.
        rom: Path to the ROM file.
        players_controllers: Controller configuration for all players.
        metadata: Game metadata (title, genre, etc.).
        guns: Configured light guns (if any).
        wheels: Configured wheels (if any).
        game_resolution: Current game resolution settings.

    Returns:
        Command: The prepared command object for running the emulator.

    """
    # Set execution directory if specified by generator
    effective_rom = rom or ""
    execution_directory = generator.executionDirectory(system.config, effective_rom)
    if execution_directory is not None:
        chdir(execution_directory)

    # Generate the command line for emulator execution

    cmd = generator.generate(
        system,
        rom,
        players_controllers,
        metadata,
        guns,
        wheels,
        game_resolution,
    )

    # Configure MangoHUD if enabled
    if (
        system.isOptSet("hud_support")
        and Path("/usr/bin/mangohud").exists()
        and system.getOptBoolean("hud_support")
    ):
        hud_bezel = getHudBezel(
            system,
            generator,
            rom,
            game_resolution,
            controllers.guns_borders_size_name(
                guns if isinstance(guns, dict) else {}, system.config
            ),
        )
        if (
            system.isOptSet("hud") and system.config["hud"] not in ["", "none"]
        ) or hud_bezel is not None:
            if not generator.hasInternalMangoHUDCall():
                cmd.array.insert(0, "mangohud")
            cmd.env["MANGOHUD_CONFIGFILE"] = str(HUD_CONFIG)
            cmd.env["MANGOHUD_DLSYM"] = "1"

    return cmd


def _run_emulator_with_profiler(command: Any, cleanup: CleanupManager) -> int:
    """Run the emulator command with profiler management.

    Args:
        command: The command object to run.
        cleanup: Cleanup manager instance.

    Returns:
        The exit code from the emulator process.

    """
    # Run the emulator command
    return runCommand(command)


def _cleanup_system(
    resolution_changed: bool,
    system_mode: Any,
    mouse_changed: bool,
    wheel_processes: list[Any],
) -> None:
    """Restores system state after the emulator exits.

    Args:
        resolution_changed: Whether the resolution was changed.
        system_mode: The original system video mode.
        mouse_changed: Whether the mouse visibility was changed.
        wheel_processes: Wheel process handles to reset.

    """
    if resolution_changed:
        try:
            videoMode.changeMode(system_mode if system_mode is not None else "")
        except CalledProcessError as e:
            eslog.warning(f"Failed to restore video mode: {e}")
        except Exception as e:
            eslog.warning(f"Unexpected error restoring video mode: {e}")

    if mouse_changed:
        try:
            videoMode.changeMouse(False)
        except CalledProcessError as e:
            eslog.warning(f"Failed to restore mouse visibility: {e}")
        except Exception as e:
            eslog.warning(f"Unexpected error restoring mouse visibility: {e}")

    if wheel_processes:
        try:
            wheelsUtils.reset_controllers(wheel_processes)
        except Exception as e:
            eslog.error(f"Unable to reset wheel controllers: {e}")


def runCommand(command: Any) -> int:
    """Execute a command in a subprocess.

    Args:
        command: A Command object containing the command array and environment variables.

    Returns:
        The exit code of the process.

    """
    global _current_process

    if not command.array:
        return -1

    # Combine current environment with command-specific environment variables more efficiently
    envvars: dict[str, str] = environ.copy()
    envvars.update(command.env)

    eslog.debug(f"command: {command!s}")
    eslog.debug(f"command array: {_sanitize_command(command.array)!s}")
    eslog.debug(f"env: {envvars!s}")
    exitcode = -1

    try:
        # Use the command's working directory if specified
        popen_kwargs = {"env": envvars, "stdout": PIPE, "stderr": PIPE}
        if hasattr(command, "cwd") and command.cwd is not None:
            popen_kwargs["cwd"] = command.cwd
        with _process_lock:
            _current_process = Popen(command.array, **popen_kwargs)
            proc = _current_process
        # Wait for the process to complete (no timeout - games can run indefinitely)
        out, err = proc.communicate()
        exitcode = _current_process.returncode
        # Log stdout/stderr.
        if out:
            with suppress(BrokenPipeError):
                eslog.debug(
                    out.decode(errors="ignore") if isinstance(out, bytes) else out
                )
        if err:
            with suppress(BrokenPipeError):
                eslog.error(
                    err.decode(errors="ignore") if isinstance(err, bytes) else err
                )
    except BrokenPipeError:
        with suppress(BrokenPipeError):
            eslog.debug("Broken pipe when communicating with emulator process")
    except OSError as e:
        with suppress(BrokenPipeError):
            eslog.error(f"OS error when communicating with emulator process: {e}")
    except Exception as e:
        with suppress(BrokenPipeError):
            eslog.error(
                f"Unexpected error when communicating with emulator process: {e}",
                exc_info=True,
            )
    finally:
        # Ensure process resources are properly released
        with _process_lock:
            proc_to_cleanup = _current_process
            _current_process = None
        if proc_to_cleanup and proc_to_cleanup.poll() is None:
            try:
                proc_to_cleanup.terminate()
                try:
                    proc_to_cleanup.wait(timeout=5)
                except TimeoutExpired:
                    proc_to_cleanup.kill()
                    proc_to_cleanup.wait()
            except (ProcessLookupError, OSError):
                pass

    return exitcode


def getHudConfig(
    system: Emulator,
    systemName: str,
    emulator: str,
    core: str,
    _rom: str,
    gameinfos: dict[str, Any],
    bezel: str | None,
) -> str:
    """Generate the configuration string for MangoHUD.

    Args:
        system: The current system's configuration object.
        systemName: The "fancy" name of the system.
        emulator: The name of the emulator.
        core: The name of the emulator core.
        _rom: Path to the ROM file (currently unused).
        gameinfos: Game metadata (name, thumbnail).
        bezel: Path to the bezel image to be used as a background.

    Returns:
        The complete MangoHUD configuration string.

    """
    configstr = ""

    # Set the bezel as the background image for the HUD.
    if bezel:
        configstr = (
            f"background_image={hudConfig_protectStr(bezel)}\nlegacy_layout=false\n"
        )

    # If HUD is disabled, just make the background transparent.
    if not system.isOptSet("hud") or system.config["hud"] == "none":
        return configstr + "background_alpha=0\n"

    mode = system.config["hud"]

    # Determine HUD position from config.
    position_map = {"NW": "top-left", "NE": "top-right", "SE": "bottom-right"}
    hud_corner = system.config.get("hud_corner", "")
    hud_position = position_map.get(hud_corner, "bottom-left")

    emulatorstr = f"{emulator}/{core}" if emulator != core and core else emulator
    gameName = gameinfos.get("name", "")
    gameThumbnail = gameinfos.get("thumbnail", "")

    # Apply predefined or custom HUD configurations.
    if mode == "perf":
        configstr += (
            f"position={hud_position}\nbackground_alpha=0.9\nlegacy_layout=false\n"
            "fps\ngpu_name\nengine_version\nvulkan_driver\nresolution\nram\n"
            "gpu_stats\ngpu_temp\ncpu_stats\ncpu_temp\ncore_load"
        )
    elif mode == "game":
        configstr += (
            f"position={hud_position}\nbackground_alpha=0\nlegacy_layout=false\n"
            "font_size=32\nimage_max_width=200\nimage=%THUMBNAIL%\n"
            "custom_text=%GAMENAME%\ncustom_text=%SYSTEMNAME%\ncustom_text=%EMULATORCORE%"
        )
    elif (
        mode == "custom"
        and system.isOptSet("hud_custom")
        and system.config["hud_custom"]
    ):
        configstr += system.config["hud_custom"].replace("\\n", "\n")
    else:
        configstr += "background_alpha=0\n"

    # Replace placeholders with actual values.
    configstr = configstr.replace("%SYSTEMNAME%", hudConfig_protectStr(systemName))
    configstr = configstr.replace("%GAMENAME%", hudConfig_protectStr(gameName))
    configstr = configstr.replace("%EMULATORCORE%", hudConfig_protectStr(emulatorstr))
    return configstr.replace("%THUMBNAIL%", hudConfig_protectStr(gameThumbnail))
