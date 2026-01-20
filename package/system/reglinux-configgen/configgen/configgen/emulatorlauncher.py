#!/usr/bin/env python3
"""Emulator launcher for the Reglinux distribution.

It is responsible for preparing the environment and launching the emulator
with the appropriate configurations.
"""

from argparse import ArgumentParser
from contextlib import suppress
from os import X_OK, access, chdir, environ
from pathlib import Path
from signal import SIGINT, SIGTERM, signal
from subprocess import PIPE, Popen, call
from threading import Thread
from time import sleep
from typing import Any

import configgen.bezel.bezel_base as bezelsUtil
from configgen import controllers
from configgen.client import regmsg_connect
from configgen.controllers import Evmapy
from configgen.emulator import Emulator
from configgen.generator_importer import getGenerator
from configgen.systemFiles import SAVES
from configgen.utils import gunsUtils, videoMode, wheelsUtils, windows_manager, zar
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

profiler = None

# Profiling Instructions:
# To enable profiling for performance analysis, follow these steps:
# 1) Create a marker file: `touch /var/run/emulatorlauncher.perf`
# 2) Start a game, which will trigger this script.
# 3) After exiting the game, a profile data file will be generated at /var/run/emulatorlauncher.prof.
#    You can then generate a call graph image using gprof2dot:
#    `gprof2dot.py -f pstats -n 5 /var/run/emulatorlauncher.prof -o emulatorlauncher.dot`
#    (You might need to download gprof2dot: `wget https://raw.githubusercontent.com/jrfonseca/gprof2dot/master/gprof2dot.py`)
# 4) Convert the .dot file to a PNG image:
#    `dot -Tpng emulatorlauncher.dot -o emulatorlauncher.png`
# 5) Alternatively, you can use an online pstats viewer like https://nejc.saje.info/pstats-viewer.html
#    to analyze the `/var/run/emulatorlauncher.prof` file.

# Enable the profiler if the performance marker file exists.
if Path("/var/run/emulatorlauncher.perf").exists():
    import cProfile

    profiler = cProfile.Profile()
    profiler.enable()

# Global process variable to hold the emulator process.
proc = None


def main(args: Any, maxnbplayers: int) -> int:
    """Entry point to start a ROM, with optional mounting of .zar archive files.

    If the input ROM file is a .zar archive, this function mounts it using zar.zar_begin(),
    retrieves the actual ROM path (in case of a single-file archive), and launches the ROM.
    After execution, it ensures the archive is properly unmounted with zar.zar_end().

    Args:
        args (Namespace): Argument object containing at least `rom` (ROM file path).
        maxnbplayers (int): Maximum number of players supported for this game.

    Returns:
        int: Exit code from the ROM launcher.

    """
    # Connect ZeroMQ
    regmsg_connect()

    # Get the file extension in lowercase
    extension = Path(args.rom).suffix[1:].lower()

    # Check if it is a .zar archive
    if extension == "zar":
        eslog.debug(f"Processing zar archive {Path(args.rom).name}")
        exitCode = 0
        need_end = False
        rommountpoint = None

        try:
            # Mount the archive and get the actual ROM path
            need_end, rommountpoint, rom = zar.zar_begin(args.rom)
            eslog.debug(f"Zar archive mounted successfully {rommountpoint}")

            # Launch the game using the mounted ROM
            exitCode = start_rom(args, maxnbplayers, rom, args.rom)

        finally:
            # Unmount the archive after the game ends
            if need_end and rommountpoint is not None:
                zar.zar_end(rommountpoint)
                eslog.debug(f"Zar archive unmounted {rommountpoint}")

        return exitCode

    # If it's not a .zar file, launch the ROM directly
    eslog.debug(f"Launching ROM directly {Path(args.rom).name}")
    return start_rom(args, maxnbplayers, args.rom, args.rom)


def _start_evmapy_async(
    system: Any,
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
        system (str): The system identifier (e.g., "nes", "snes").
        emulator (str): The emulator name.
        core (str): The emulator core name.
        rom (str): Path used for specific ROM configuration.
        players_controllers (list): Controller configuration for all players.
        guns (list): Configured light guns (if any).

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


def _configure_controllers(args: Any, maxnbplayers: int) -> dict[str, Any]:
    """Configure controllers based on command-line arguments."""
    controllersInput: list[dict[str, Any]] = []
    for p in range(1, maxnbplayers + 1):
        ci = {
            "index": getattr(args, f"p{p}index"),
            "guid": getattr(args, f"p{p}guid"),
            "name": getattr(args, f"p{p}name"),
            "devicepath": getattr(args, f"p{p}devicepath"),
            "nbbuttons": getattr(args, f"p{p}nbbuttons"),
            "nbhats": getattr(args, f"p{p}nbhats"),
            "nbaxes": getattr(args, f"p{p}nbaxes"),
        }
        controllersInput.append(ci)

    return controllers.load_controller_config(controllersInput)


def _setup_system_emulator(args: Any, rom: str) -> Any:
    """Initialize system and emulator configurations."""
    systemName = args.system
    eslog.debug(f"Running system: {systemName}")
    system = Emulator(systemName, args.rom)

    if args.emulator is not None:
        system.config["emulator"] = args.emulator
        system.config["emulator_forced"] = True
    if args.core is not None:
        system.config["core"] = args.core
        system.config["core_forced"] = True

    debugDisplay = system.config.copy()
    if "retroachievements.password" in debugDisplay:
        debugDisplay["retroachievements.password"] = "***"
    eslog.debug(f"Settings: {debugDisplay}")

    if "emulator" in system.config:
        core_info = (
            f", core: {system.config['core']}" if "core" in system.config else ""
        )
        eslog.debug(f"emulator: {system.config['emulator']}{core_info}")

    return system


def _configure_special_devices(
    args: Any,
    system: Any,
    rom: str,
    metadata: Any,
    players_controllers: Any,
) -> tuple[dict[str, Any] | list[Any], dict[str, Any] | list[Any], Any, Any]:
    """Configure light guns and racing wheels."""
    guns: dict[str, Any] | list[Any] = []
    if not system.isOptSet("use_guns") and args.lightgun:
        system.config["use_guns"] = True
    if system.isOptSet("use_guns") and system.getOptBoolean("use_guns"):
        guns = controllers.getGuns()
        core = system.config.get("core")
        gunsUtils.precalibration(system.name, system.config["emulator"], core, rom)
    else:
        eslog.info("Guns disabled.")

    wheel_processes: Any = None
    wheels: dict[str, Any] | list[Any]
    if not system.isOptSet("use_wheels") and args.wheel:
        system.config["use_wheels"] = True
    if system.isOptSet("use_wheels") and system.getOptBoolean("use_wheels"):
        device_infos = controllers.getDevicesInformation()
        (wheel_processes, players_controllers, device_infos) = (
            wheelsUtils.reconfigure_controllers(
                players_controllers,
                system,
                rom,
                metadata,
            )
        )
        wheels = wheelsUtils.get_wheels_from_device_infos(device_infos)
    else:
        eslog.info("Wheels disabled.")
        wheels = []

    # Corrigindo o tipo para garantir consistência
    guns = guns if isinstance(guns, (list, dict)) else []
    wheels = wheels if isinstance(wheels, (list, dict)) else []

    # Garantir que o retorno tenha os tipos corretos
    guns_result: dict[str, Any] | list[Any] = (
        guns if isinstance(guns, (dict, list)) else []
    )
    wheels_result: dict[str, Any] | list[Any] = (
        wheels if isinstance(wheels, (dict, list)) else []
    )

    return guns_result, wheels_result, wheel_processes, players_controllers


def _setup_video_and_mouse(
    system: Any,
    generator: Any,
    rom: str,
) -> tuple[Any, bool, bool, dict[str, int]]:
    """Set up video mode and mouse visibility for the game."""
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


def _apply_commandline_options(args: Any, system: Any) -> None:
    """Apply command-line options like netplay and save states to the system config."""
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


def _setup_environment_variables(system: Any) -> None:
    """Set up environment variables for the emulator."""
    system.config["sdlvsync"] = (
        "0"
        if system.isOptSet("sdlvsync") and not system.getOptBoolean("sdlvsync")
        else "1"
    )
    environ["SDL_RENDER_VSYNC"] = system.config["sdlvsync"]

    # Set keyboard and locale environment variables to prevent xkbcommon errors
    # Use minimal locale to avoid compose file issues
    environ["LC_ALL"] = "C"
    environ["LANG"] = "C"
    environ["LANGUAGE"] = "C"
    environ["LC_CTYPE"] = "C"

    # Set XKB configuration to prevent compose file errors
    environ["XKB_DEFAULT_OPTIONS"] = ""
    # Also set XKB to avoid compose file lookup
    environ["XKB_LOG_LEVEL"] = "critical"


def _execute_external_scripts(system: Any, rom: str, event_type: str) -> None:
    """Execute external scripts based on the event type."""
    effectiveCore = system.config.get("core", "")
    effectiveRom = rom or ""

    script_directories = [
        Path("/usr/share/reglinux/configgen/scripts"),
        Path("/userdata/system/scripts"),
    ]

    # For gameStart events, we want the first directory to be user scripts
    if event_type == "gameStop":
        script_directories.reverse()

    for directory in script_directories:
        callExternalScripts(
            str(directory),
            event_type,
            [system.name, system.config["emulator"], effectiveCore, effectiveRom],
        )


def _create_save_directory(system: Any) -> None:
    """Create the save directory for the system if it doesn't exist."""
    dirname = SAVES / system.name
    if not dirname.exists():
        dirname.mkdir(parents=True, exist_ok=True)


def _cleanup_hud_config():
    """Clean up the temporary HUD config file."""
    try:
        hud_config_path = Path("/var/run/hud.config")
        if hud_config_path.exists():
            hud_config_path.unlink()
    except Exception as e:
        eslog.warning(f"Could not remove HUD config file: {e}")


def _configure_hud(
    system: Any,
    generator: Any,
    cmd: Any,
    args: Any,
    rom: str,
    game_resolution: dict[str, int],
    guns: Any,
) -> None:
    """Configure and enable MangoHUD if supported."""
    if not (
        system.isOptSet("hud_support")
        and Path("/usr/bin/mangohud").exists()
        and system.getOptBoolean("hud_support")
    ):
        return

    hud_bezel = getHudBezel(
        system,
        generator,
        rom,
        game_resolution,
        controllers.guns_borders_size_name(guns, system.config),
    )
    if (
        system.isOptSet("hud") and system.config["hud"] not in ["", "none"]
    ) or hud_bezel is not None:
        gameinfos = extractGameInfosFromXml(args.gameinfoxml)
        cmd.env["MANGOHUD_DLSYM"] = "1"
        effective_core = system.config.get("core", "")
        hudconfig = getHudConfig(
            system,
            args.systemname,
            system.config["emulator"],
            effective_core,
            rom,
            gameinfos,
            hud_bezel,
        )
        hud_config_path = Path("/var/run/hud.config")
        Path(hud_config_path).write_text(hudconfig)
        cmd.env["MANGOHUD_CONFIGFILE"] = str(hud_config_path)
        if not generator.hasInternalMangoHUDCall():
            cmd.array.insert(0, "mangohud")


def _setup_evmapy_and_compositor(
    generator: Any,
    system: Any,
    rom: str,
    players_controllers: Any,
    guns: Any,
    args: Any,
    rom_configuration: dict[str, Any],
) -> Any:
    """Set up Evmapy and compositor before launching the emulator.

    Args:
        generator (Generator): Emulator-specific generator instance.
        system (Emulator): System configuration object.
        rom (str): Path to the ROM file.
        players_controllers (list): Controller configuration for all players.
        guns (list): Configured light guns (if any).
        args (Namespace): Command-line arguments passed to the launcher.
        rom_configuration (str): ROM configuration path (may differ if archive is used).

    Returns:
        threading.Thread: The thread running Evmapy.

    """
    # Start Evmapy in a separate thread (non-blocking)
    evmapy_thread = _start_evmapy_async(
        args.system,
        system.config["emulator"],
        system.config.get("core", ""),
        rom,
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
    system: Any,
    rom: str,
    players_controllers: Any,
    metadata: Any,
    guns: Any,
    wheels: Any,
    game_resolution: dict[str, int],
    args: Any,
) -> Any:
    """Prepare the emulator command with all necessary configurations.

    Args:
        generator (Generator): Emulator-specific generator instance.
        system (Emulator): System configuration object.
        rom (str): Path to the ROM file.
        players_controllers (list): Controller configuration for all players.
        metadata (dict): Game metadata (title, genre, etc.).
        guns (list): Configured light guns (if any).
        wheels (list): Configured wheels (if any).
        game_resolution (dict): Current game resolution settings.
        args (Namespace): Command-line arguments passed to the launcher.

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
    _configure_hud(system, generator, cmd, args, rom, game_resolution, guns)

    return cmd


def _run_emulator_with_profiler(cmd: Any) -> int:
    """Run the emulator command with profiler management.

    Args:
        cmd (Command): The command object to run.

    Returns:
        int: The exit code from the emulator process.

    """
    global profiler

    # Disable profiler while emulator runs
    if profiler:
        profiler.disable()

    # Run the emulator command
    exitCode = runCommand(cmd)

    # Re-enable profiler after emulator exit
    if profiler:
        profiler.enable()

    return exitCode


def _cleanup_emulator_resources(
    generator: Any,
    evmapy_thread: Any,
    system: Any,
) -> None:
    """Clean up resources after the emulator exits.

    Args:
        generator (Generator): Emulator-specific generator instance.
        evmapy_thread (Thread): The thread running Evmapy.
        system (Emulator): System configuration object.

    """
    # Stop Evmapy gracefully
    Evmapy.stop()
    if evmapy_thread and evmapy_thread.is_alive():
        evmapy_thread.join(timeout=1)  # prevent zombie threads

    # Stop compositor if it was started
    if generator.requiresWayland() or generator.requiresX11():
        windows_manager.stop_compositor(generator, system)


def _launch_emulator_process(
    generator: Any,
    system: Any,
    rom: str,
    players_controllers: Any,
    metadata: Any,
    guns: Any,
    wheels: Any,
    game_resolution: dict[str, int],
    args: Any,
    rom_configuration: dict[str, Any],
) -> int:
    """Handle the actual emulator launch process inside a try/finally block.

    This function takes care of:
    - Starting Evmapy asynchronously (non-blocking).
    - Launching the emulator with the correct environment and command line.
    - Managing compositor (Wayland/X11) if required.
    - Handling HUD configuration.
    - Ensuring proper cleanup after the emulator exits.

    Args:
        generator (Generator): Emulator-specific generator instance.
        system (Emulator): System configuration object.
        rom (str): Path to the ROM file.
        players_controllers (list): Controller configuration for all players.
        metadata (dict): Game metadata (title, genre, etc.).
        guns (list): Configured light guns (if any).
        wheels (list): Configured wheels (if any).
        game_resolution (dict): Current game resolution settings.
        args (Namespace): Command-line arguments passed to the launcher.
        rom_configuration (str): ROM configuration path (may differ if archive is used).

    Returns:
        int: Exit code from the emulator process.

    """
    global profiler
    exitCode = -1
    evmapy_thread = None

    try:
        # Setup Evmapy and compositor
        evmapy_thread = _setup_evmapy_and_compositor(
            generator,
            system,
            rom,
            players_controllers,
            guns,
            args,
            rom_configuration,
        )

        # Prepare the emulator command
        cmd = _prepare_emulator_command(
            generator,
            system,
            rom,
            players_controllers,
            metadata,
            guns,
            wheels,
            game_resolution,
            args,
        )

        # Run the emulator with profiler management
        exitCode = _run_emulator_with_profiler(cmd)

    finally:
        # Clean up resources
        _cleanup_emulator_resources(generator, evmapy_thread, system)
        # Clean up HUD config file
        _cleanup_hud_config()

    return exitCode


def _cleanup_system(
    resolution_changed: bool,
    system_mode: Any,
    mouse_changed: bool,
    wheel_processes: Any,
) -> None:
    """Restores system state after the emulator exits."""
    import subprocess  # Import subprocess here to resolve "subprocess" is not defined errors

    if resolution_changed:
        try:
            videoMode.changeMode(system_mode if system_mode is not None else "")
        except subprocess.CalledProcessError as e:
            eslog.warning(f"Failed to restore video mode: {e}")
        except Exception as e:
            eslog.warning(f"Unexpected error restoring video mode: {e}")
    if mouse_changed:
        try:
            videoMode.changeMouse(False)
        except subprocess.CalledProcessError as e:
            eslog.warning(f"Failed to restore mouse visibility: {e}")
        except Exception as e:
            eslog.warning(f"Unexpected error restoring mouse visibility: {e}")
    if wheel_processes:
        try:
            wheelsUtils.reset_controllers(wheel_processes)
        except Exception as e:
            eslog.error(f"Unable to reset wheel controllers: {e}")


def start_rom(
    args: Any,
    maxnbplayers: int,
    rom: str,
    rom_configuration: dict[str, Any],
) -> int:
    """Prepare the system and launch the emulator for a given ROM.

    This function handles:
    - Controller configuration.
    - System and emulator settings.
    - Light gun and wheel setup.
    - Video mode adjustments.
    - Bezel and HUD generation.
    - Pre/post emulation script execution.
    - Launching the emulator.

    Args:
        args (Namespace): The command-line arguments.
        maxnbplayers (int): The maximum number of players.
        rom (str): The path to the ROM file.
        rom_configuration (str): The ROM file path used for specific configurations.

    Returns:
        int: The exit code from the emulator process.

    """
    # Initial setup
    players_controllers = _configure_controllers(args, maxnbplayers)
    system = _setup_system_emulator(args, rom)
    metadata = controllers.getGamesMetaData(system.name, rom)
    guns, wheels, wheel_processes, players_controllers = _configure_special_devices(
        args,
        system,
        rom,
        metadata,
        players_controllers,
    )
    generator = getGenerator(system.config["emulator"])

    exit_code = -1
    resolution_changed, mouse_changed = False, False
    system_mode = videoMode.getCurrentMode()

    try:
        # Configure video and mouse settings
        system_mode, resolution_changed, mouse_changed, game_resolution = (
            _setup_video_and_mouse(system, generator, rom)
        )

        # Create save directory
        _create_save_directory(system)

        # Apply command-line options
        _apply_commandline_options(args, system)

        # Setup environment variables
        _setup_environment_variables(system)

        # Execute pre-launch scripts
        _execute_external_scripts(system, rom, "gameStart")

        eslog.debug("==== Running emulator ====")
        exit_code = _launch_emulator_process(
            generator,
            system,
            rom,
            players_controllers,
            metadata,
            guns,
            wheels,
            game_resolution,
            args,
            rom_configuration,
        )

        # Execute post-launch scripts
        _execute_external_scripts(system, rom, "gameStop")

    finally:
        _cleanup_system(resolution_changed, system_mode, mouse_changed, wheel_processes)

    return exit_code


def _cleanup_temp_files(*temp_files: str) -> None:
    """Clean up temporary files created during bezel processing.

    Args:
        *temp_files: Variable number of temporary file paths to cleanup

    """
    for temp_file in temp_files:
        try:
            if temp_file and Path(temp_file).exists():
                Path(temp_file).unlink()
        except Exception as e:
            eslog.warning(f"Could not remove temporary file {temp_file}: {e}")


def getHudBezel(
    system: Any,
    generator: Any,
    rom: str,
    game_resolution: dict[str, int],
    borders_size: Any,
) -> Any:
    """Determine and prepare the appropriate bezel image for the HUD.

    It checks for bezel compatibility (aspect ratio, coverage) and resizes,
    tattoos, or adds borders to the image as needed.

    Args:
        system (Emulator): The current system's configuration object.
        generator (Generator): The emulator-specific generator.
        rom (str): Path to the ROM file.
        game_resolution (dict): The current game resolution.
        borders_size (str): The size of the gun borders, if any.

    Returns:
        str|None: The path to the final bezel image file, or None if no bezel should be used.

    """
    # Import json here to ensure it's always available within the function scope
    # for error handling, preventing "json is possibly unbound" diagnostic.
    import json

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
            overlay_png_file = Path("/tmp/bezel_transhud_black.png")
            overlay_info_file = Path("/tmp/bezel_transhud_black.info")
            temp_files.extend([str(overlay_png_file), str(overlay_info_file)])
            bezelsUtil.createTransparentBezel(
                str(overlay_png_file),
                game_resolution["width"],
                game_resolution["height"],
            )

            w, h = game_resolution["width"], game_resolution["height"]
            Path(overlay_info_file).write_text(f'{{"width":{w}, "height":{h}, "opacity":1.0, "messagex":0.22, "messagey":0.12}}')
        else:
            # A bezel is configured, so let's find its files.
            eslog.debug(
                f"HUD enabled. Trying to apply the bezel {system.config['bezel']}",
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
            overlay_info_file, overlay_png_file = bz_infos["info"], bz_infos["png"]

        # --- Bezel Validation ---
        infos = {}  # Initialize infos here to ensure it's always defined
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
            eslog.info(f"Bezel size read from {overlay_info_file}")
        elif overlay_png_file and isinstance(overlay_png_file, str):
            bezel_width: int = bezelsUtil.fast_image_size(overlay_png_file)[0]
            bezel_height: int = bezelsUtil.fast_image_size(overlay_png_file)[1]
            eslog.info(f"Bezel size read from {overlay_png_file}")
        else:
            eslog.error(f"Invalid overlay PNG file: {overlay_png_file}")
            return None

        # Define validation thresholds.
        max_ratio_delta = 0.01  # Max difference between screen and bezel aspect ratio.

        screen_ratio: float = game_resolution["width"] / game_resolution["height"]
        bezel_ratio: float = bezel_width / bezel_height

        # Validate aspect ratio (unless gun borders are being added, which might need a different ratio).
        if borders_size is None and abs(screen_ratio - bezel_ratio) > max_ratio_delta:
            eslog.debug(
                f"Screen ratio ({screen_ratio}) is too far from the bezel one ({bezel_ratio})",
            )
            return None

        # --- Bezel Processing ---
        # Resize the bezel image if it doesn't match the screen resolution.
        bezel_stretch = system.isOptSet("bezel_stretch") and system.getOptBoolean(
            "bezel_stretch",
        )
        if (
            bezel_width != game_resolution["width"]
            or bezel_height != game_resolution["height"]
        ):
            eslog.debug("Bezel needs to be resized")
            output_png_file = Path("/tmp/bezel.png")
            temp_files.append(str(output_png_file))
            if overlay_png_file and isinstance(overlay_png_file, (str, Path)):
                try:
                    bezelsUtil.resizeImage(
                        str(overlay_png_file),
                        str(output_png_file),
                        game_resolution["width"],
                        game_resolution["height"],
                        bezel_stretch,
                    )
                    overlay_png_file = output_png_file
                except Exception as e:
                    eslog.error(f"Failed to resize the image: {e}")
                    return None
            else:
                eslog.error(f"Invalid overlay PNG file for resize: {overlay_png_file}")
                return None

        # Apply a "tattoo" (watermark/logo) to the bezel if configured.
        if system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0":
            output_png_file = Path("/tmp/bezel_tattooed.png")
            temp_files.append(str(output_png_file))
            if overlay_png_file and isinstance(overlay_png_file, (str, Path)):
                bezelsUtil.tatooImage(
                    str(overlay_png_file),
                    str(output_png_file),
                    system,
                )
                overlay_png_file = output_png_file
            else:
                eslog.error(f"Invalid overlay PNG file for tattoo: {overlay_png_file}")
                return None

        # Draw gun borders on the bezel if required.
        if borders_size is not None:
            eslog.debug("Drawing gun borders")
            output_png_file = Path("/tmp/bezel_gunborders.png")
            temp_files.append(str(output_png_file))
            inner_size, outer_size = bezelsUtil.gun_borders_size(borders_size)
            color = bezelsUtil.gunsBordersColorFomConfig(system.config)
            if overlay_png_file and isinstance(overlay_png_file, (str, Path)):
                bezelsUtil.gunBorderImage(
                    str(overlay_png_file),
                    str(output_png_file),
                    inner_size,
                    outer_size,
                    color,
                )
                overlay_png_file = output_png_file
            else:
                eslog.error(
                    f"Invalid overlay PNG file for gun border: {overlay_png_file}",
                )
                return None

        eslog.debug(f"Applying bezel {overlay_png_file}")
        return overlay_png_file

    finally:
        # Clean up temporary files
        _cleanup_temp_files(*temp_files)


def extractGameInfosFromXml(xml: Any) -> dict[str, Any]:
    """Parse a game information XML file to extract game name and thumbnail.

    Args:
        xml (str): Path to the game info XML file.

    Returns:
        dict: A dictionary containing 'name' and 'thumbnail' if found.

    """
    import xml.etree.ElementTree as ET

    vals: dict[str, Any] = {}
    try:
        # ET.parse will handle the file opening/closing internally
        infos = ET.parse(xml)
        name_elem = infos.find("./game/name")
        if name_elem is not None:
            vals["name"] = name_elem.text
        thumbnail_elem = infos.find("./game/thumbnail")
        if thumbnail_elem is not None:
            vals["thumbnail"] = thumbnail_elem.text
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
        folder (str): The directory containing the scripts.
        event (str): The event name (e.g., "gameStart", "gameStop").
        args (list): A list of arguments to pass to the scripts.

    """
    if not Path(folder).is_dir():
        return
    try:
        file_list = sorted(
            Path(folder).iterdir(),
        )  # Sort for predictable execution order.
    except OSError as e:
        eslog.warning(f"Could not read directory {folder}: {e}")
        return

    for file in file_list:
        filepath = Path(folder) / file
        if Path(filepath).is_dir():
            callExternalScripts(
                str(filepath),
                event,
                args,
            )  # Recurse into subdirectories.
        elif access(filepath, X_OK):
            with suppress(BrokenPipeError):
                eslog.debug(f"Calling external script: {[filepath, event] + args!s}")
            try:
                result = call([filepath, event] + args)
                if result != 0:
                    with suppress(BrokenPipeError):
                        eslog.warning(
                            f"External script {filepath} returned non-zero exit code: {result}",
                        )
            except OSError as e:
                with suppress(BrokenPipeError):
                    eslog.error(f"Failed to execute external script {filepath}: {e}")
            except Exception as e:
                with suppress(BrokenPipeError):
                    eslog.error(
                        f"Unexpected error executing external script {filepath}: {e}",
                    )


def hudConfig_protectStr(text: str) -> str:
    """Return an empty string if the input is None, otherwise return the input.

    Args:
        text (str): The string to protect.

    Returns:
        str: The original string or an empty string.

    """
    return text or ""


def getHudConfig(
    system: Any,
    systemName: str,
    emulator: str,
    core: str,
    rom: str,
    gameinfos: Any,
    bezel: Any,
) -> str:
    """Generate the configuration string for MangoHUD.

    Args:
        system (Emulator): The current system's configuration object.
        systemName (str): The "fancy" name of the system.
        emulator (str): The name of the emulator.
        core (str): The name of the emulator core.
        rom (str): Path to the ROM file.
        gameinfos (dict): Game metadata (name, thumbnail).
        bezel (str|None): Path to the bezel image to be used as a background.

    Returns:
        str: The complete MangoHUD configuration string.

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
            "custom_text=%GAMENAME%\ncustom_text=%SYSTEMNAME%\ncustom_text=%EMULATORCORE%\n"
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
        # Fallback to hiding the HUD if the mode is invalid.
        configstr += "background_alpha=0\n"

    # Replace placeholders with actual values.
    configstr = configstr.replace("%SYSTEMNAME%", hudConfig_protectStr(systemName))
    configstr = configstr.replace("%GAMENAME%", hudConfig_protectStr(gameName))
    configstr = configstr.replace("%EMULATORCORE%", hudConfig_protectStr(emulatorstr))
    return configstr.replace("%THUMBNAIL%", hudConfig_protectStr(gameThumbnail))


def runCommand(command: Any) -> int:
    """Execute a command in a subprocess.

    Args:
        command (Command): A Command object containing the command array and environment variables.

    Returns:
        int: The exit code of the process.

    """
    global proc

    if not command.array:
        return -1

    # Combine current environment with command-specific environment variables.
    envvars: dict[str, str] = {**environ, **command.env}

    eslog.debug(f"command: {command!s}")
    eslog.debug(f"command: {command.array!s}")
    eslog.debug(f"env: {envvars!s}")
    exitcode = -1

    proc = Popen(command.array, env=envvars, stdout=PIPE, stderr=PIPE)
    try:
        out, err = proc.communicate()
        exitcode = proc.returncode
        # Decode and log stdout/stderr.
        if out:
            with suppress(BrokenPipeError):
                eslog.debug(out.decode(errors="ignore"))
        if err:
            with suppress(BrokenPipeError):
                eslog.error(err.decode(errors="ignore"))
    except BrokenPipeError:
        # This can happen if the parent process (like `head`) closes the pipe.
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
        if proc and proc.poll() is None:  # Process is still running
            with suppress(ProcessLookupError):
                proc.kill()
        proc = None  # Clear the global reference

    return exitcode


def signal_handler(signal: Any, frame: Any) -> None:
    """Handle termination signals (like Ctrl+C) to gracefully kill the emulator process."""
    global proc
    eslog.debug("Exiting due to signal")
    if proc:
        eslog.debug("Killing emulator process")
        proc.kill()
    exit(0)


if __name__ == "__main__":
    # Register signal handler for graceful termination.
    signal(SIGINT, signal_handler)
    signal(SIGTERM, signal_handler)

    # --- Argument Parsing ---
    parser = ArgumentParser(description="Emulator Launcher Script")

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

    # --- Finalization ---
    # If profiling was enabled, save the results.
    if profiler:
        try:
            profiler.disable()
            profiler.dump_stats(str(Path("/var/run/emulatorlauncher.prof")))
        except Exception as e:
            eslog.error(f"Error dumping profiler stats: {e}")

    # A short delay can help ensure resources (like GPU memory) are fully released before returning to the frontend.
    sleep(1)
    with suppress(BrokenPipeError):
        eslog.debug(f"Exiting configgen with status {exitcode!s}")

    exit(exitcode)
