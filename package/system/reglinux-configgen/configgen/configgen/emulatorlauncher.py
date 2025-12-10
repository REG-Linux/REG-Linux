#!/usr/bin/env python3
"""
This script is the emulator launcher for the Reglinux distribution.
It is responsible for preparing the environment and launching the emulator
with the appropriate configurations.
"""

from os import path, environ, chdir, makedirs, access, listdir, X_OK
from argparse import ArgumentParser
from signal import signal, SIGINT, SIGTERM
from time import sleep
from subprocess import Popen, PIPE, call
from configgen.systemFiles import SAVES
from sys import exit
from configgen.Emulator import Emulator
from threading import Thread
from configgen.controllers import Evmapy
from configgen.GeneratorImporter import getGenerator
import configgen.utils.videoMode as videoMode
import configgen.utils.gunsUtils as gunsUtils
import configgen.utils.wheelsUtils as wheelsUtils
import configgen.utils.windowsManager as windowsManager
import configgen.utils.bezels as bezelsUtil
import configgen.controllers as controllers
import configgen.utils.zar as zar
from configgen.utils.logger import get_logger

from configgen.utils.regmsgclient import regmsg_connect

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
if path.exists("/var/run/emulatorlauncher.perf"):
    import cProfile

    profiler = cProfile.Profile()
    profiler.enable()

# Global process variable to hold the emulator process.
proc = None


def main(args, maxnbplayers):
    """
    Entry point to start a ROM, with optional mounting of .zar archive files.

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
    extension = path.splitext(args.rom)[1][1:].lower()

    # Check if it is a .zar archive
    if extension == "zar":
        eslog.debug(f"Processing zar archive {path.basename(args.rom)}")
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

    else:
        # If it's not a .zar file, launch the ROM directly
        eslog.debug(f"Launching ROM directly {path.basename(args.rom)}")
        return start_rom(args, maxnbplayers, args.rom, args.rom)


def _start_evmapy_async(system, emulator, core, romConfig, playersControllers, guns):
    """
    Starts Evmapy asynchronously in a background thread.

    This prevents the emulator startup from being delayed by Evmapy initialization.
    Evmapy will run in parallel while the emulator is already loading.

    Args:
        system (str): The system identifier (e.g., "nes", "snes").
        emulator (str): The emulator name.
        core (str): The emulator core name.
        romConfig (str): Path used for specific ROM configuration.
        playersControllers (list): Controller configuration for all players.
        guns (list): Configured light guns (if any).

    Returns:
        threading.Thread: The thread running Evmapy.
    """

    def worker():
        try:
            Evmapy.start(system, emulator, core, romConfig, playersControllers, guns)
        except Exception as e:
            eslog.error(f"Evmapy failed: {e}", exc_info=True)

    # Start the Evmapy worker in background mode (daemon thread).
    t = Thread(target=worker, daemon=True)
    t.start()
    return t


def _configure_controllers(args, maxnbplayers):
    """Configures controllers based on command-line arguments."""
    controllersInput = []
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

    playersControllers = controllers.load_controller_config(controllersInput)
    return playersControllers


def _setup_system_emulator(args, romConfiguration):
    """Initializes system and emulator configurations."""
    systemName = args.system
    eslog.debug(f"Running system: {systemName}")
    system = Emulator(systemName, romConfiguration)

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


def _configure_special_devices(args, system, rom, metadata, playersControllers):
    """Configures light guns and racing wheels."""
    if not system.isOptSet("use_guns") and args.lightgun:
        system.config["use_guns"] = True
    if system.isOptSet("use_guns") and system.getOptBoolean("use_guns"):
        guns = controllers.getGuns()
        core = system.config.get("core")
        gunsUtils.precalibration(system.name, system.config["emulator"], core, rom)
    else:
        eslog.info("Guns disabled.")
        guns = []

    wheelProcesses = None
    if not system.isOptSet("use_wheels") and args.wheel:
        system.config["use_wheels"] = True
    if system.isOptSet("use_wheels") and system.getOptBoolean("use_wheels"):
        deviceInfos = controllers.getDevicesInformation()
        (wheelProcesses, playersControllers, deviceInfos) = (
            wheelsUtils.reconfigureControllers(
                playersControllers, system, rom, metadata
            )
        )
        wheels = wheelsUtils.getWheelsFromDevicesInfos(deviceInfos)
    else:
        eslog.info("Wheels disabled.")
        wheels = []

    return guns, wheels, wheelProcesses, playersControllers


def _setup_video_and_mouse(system, generator, rom):
    """Sets up video mode and mouse visibility for the game."""
    wantedGameMode = generator.getResolutionMode(system.config)
    systemMode = videoMode.getCurrentMode()
    resolutionChanged = False
    mouseChanged = False

    newsystemMode = systemMode
    if system.config.get("videomode", "default") in ["", "default"]:
        eslog.debug("==== minTomaxResolution ====")
        eslog.debug(f"Video mode before minmax: {systemMode}")
        videoMode.minTomaxResolution()
        newsystemMode = videoMode.getCurrentMode()
        if newsystemMode != systemMode:
            resolutionChanged = True

    eslog.debug(f"Current video mode: {newsystemMode}")
    eslog.debug(f"Wanted video mode: {wantedGameMode}")

    if wantedGameMode != "default" and wantedGameMode != newsystemMode:
        videoMode.changeMode(wantedGameMode)
        resolutionChanged = True
    gameResolution = videoMode.getCurrentResolution()

    if generator.getMouseMode(system.config, rom):
        mouseChanged = True
        videoMode.changeMouse(True)

    return systemMode, resolutionChanged, mouseChanged, gameResolution


def _apply_commandline_options(args, system):
    """Applies command-line options like netplay and save states to the system config."""
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


def _setup_environment_variables(system):
    """Sets up environment variables for the emulator."""
    system.config["sdlvsync"] = (
        "0"
        if system.isOptSet("sdlvsync") and not system.getOptBoolean("sdlvsync")
        else "1"
    )
    environ["SDL_RENDER_VSYNC"] = system.config["sdlvsync"]


def _execute_external_scripts(system, rom, event_type):
    """Executes external scripts based on the event type."""
    effectiveCore = system.config.get("core", "")
    effectiveRom = rom or ""

    script_directories = [
        "/usr/share/reglinux/configgen/scripts",
        "/userdata/system/scripts",
    ]

    # For gameStart events, we want the first directory to be user scripts
    if event_type == "gameStop":
        script_directories.reverse()

    for directory in script_directories:
        callExternalScripts(
            directory,
            event_type,
            [system.name, system.config["emulator"], effectiveCore, effectiveRom],
        )


def _create_save_directory(system):
    """Creates the save directory for the system if it doesn't exist."""
    dirname = path.join(SAVES, system.name)
    if not path.exists(dirname):
        makedirs(dirname)


def _cleanup_hud_config():
    """Cleans up the temporary HUD config file."""
    try:
        if path.exists("/var/run/hud.config"):
            from os import remove

            remove("/var/run/hud.config")
    except Exception as e:
        eslog.warning(f"Could not remove HUD config file: {e}")


def _configure_hud(system, generator, cmd, args, rom, gameResolution, guns):
    """Configures and enables MangoHUD if supported."""
    if not (
        system.isOptSet("hud_support")
        and path.exists("/usr/bin/mangohud")
        and system.getOptBoolean("hud_support")
    ):
        return

    hud_bezel = getHudBezel(
        system,
        generator,
        rom,
        gameResolution,
        controllers.gunsBordersSizeName(guns, system.config),
    )
    if (
        system.isOptSet("hud") and system.config["hud"] not in ["", "none"]
    ) or hud_bezel is not None:
        gameinfos = extractGameInfosFromXml(args.gameinfoxml)
        cmd.env["MANGOHUD_DLSYM"] = "1"
        effectiveCore = system.config.get("core", "")
        hudconfig = getHudConfig(
            system,
            args.systemname,
            system.config["emulator"],
            effectiveCore,
            rom,
            gameinfos,
            hud_bezel,
        )
        with open("/var/run/hud.config", "w") as f:
            f.write(hudconfig)
        cmd.env["MANGOHUD_CONFIGFILE"] = "/var/run/hud.config"
        if not generator.hasInternalMangoHUDCall():
            cmd.array.insert(0, "mangohud")


def _setup_evmapy_and_compositor(
    generator, system, rom, playersControllers, guns, args, romConfiguration
):
    """
    Sets up Evmapy and compositor before launching the emulator.

    Args:
        generator (Generator): Emulator-specific generator instance.
        system (Emulator): System configuration object.
        rom (str): Path to the ROM file.
        playersControllers (list): Controller configuration for all players.
        guns (list): Configured light guns (if any).
        args (Namespace): Command-line arguments passed to the launcher.
        romConfiguration (str): ROM configuration path (may differ if archive is used).

    Returns:
        threading.Thread: The thread running Evmapy.
    """
    # Start Evmapy in a separate thread (non-blocking)
    evmapy_thread = _start_evmapy_async(
        args.system,
        system.config["emulator"],
        system.config.get("core", ""),
        romConfiguration,
        playersControllers,
        guns,
    )

    # Start a compositor if required (Wayland or X11)
    if (
        generator.requiresWayland() or generator.requiresX11()
    ) and "WAYLAND_DISPLAY" not in environ:
        windowsManager.start_compositor(generator, system)

    return evmapy_thread


def _prepare_emulator_command(
    generator,
    system,
    rom,
    playersControllers,
    metadata,
    guns,
    wheels,
    gameResolution,
    args,
):
    """
    Prepares the emulator command with all necessary configurations.

    Args:
        generator (Generator): Emulator-specific generator instance.
        system (Emulator): System configuration object.
        rom (str): Path to the ROM file.
        playersControllers (list): Controller configuration for all players.
        metadata (dict): Game metadata (title, genre, etc.).
        guns (list): Configured light guns (if any).
        wheels (list): Configured wheels (if any).
        gameResolution (dict): Current game resolution settings.
        args (Namespace): Command-line arguments passed to the launcher.

    Returns:
        Command: The prepared command object for running the emulator.
    """
    # Set execution directory if specified by generator
    effectiveRom = rom or ""
    executionDirectory = generator.executionDirectory(system.config, effectiveRom)
    if executionDirectory is not None:
        chdir(executionDirectory)

    # Generate the command line for emulator execution
    cmd = generator.generate(
        system, rom, playersControllers, metadata, guns, wheels, gameResolution
    )

    # Configure MangoHUD if enabled
    _configure_hud(system, generator, cmd, args, rom, gameResolution, guns)

    return cmd


def _run_emulator_with_profiler(cmd):
    """
    Runs the emulator command with profiler management.

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


def _cleanup_emulator_resources(generator, evmapy_thread, system):
    """
    Cleans up resources after the emulator exits.

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
        windowsManager.stop_compositor(generator, system)


def _launch_emulator_process(
    generator,
    system,
    rom,
    playersControllers,
    metadata,
    guns,
    wheels,
    gameResolution,
    args,
    romConfiguration,
):
    """
    Handles the actual emulator launch process inside a try/finally block.

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
        playersControllers (list): Controller configuration for all players.
        metadata (dict): Game metadata (title, genre, etc.).
        guns (list): Configured light guns (if any).
        wheels (list): Configured wheels (if any).
        gameResolution (dict): Current game resolution settings.
        args (Namespace): Command-line arguments passed to the launcher.
        romConfiguration (str): ROM configuration path (may differ if archive is used).

    Returns:
        int: Exit code from the emulator process.
    """
    global profiler
    exitCode = -1
    evmapy_thread = None

    try:
        # Setup Evmapy and compositor
        evmapy_thread = _setup_evmapy_and_compositor(
            generator, system, rom, playersControllers, guns, args, romConfiguration
        )

        # Prepare the emulator command
        cmd = _prepare_emulator_command(
            generator,
            system,
            rom,
            playersControllers,
            metadata,
            guns,
            wheels,
            gameResolution,
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


def _cleanup_system(resolutionChanged, systemMode, mouseChanged, wheelProcesses):
    """Restores system state after the emulator exits."""
    import subprocess  # Import subprocess here to resolve "subprocess" is not defined errors

    if resolutionChanged:
        try:
            videoMode.changeMode(systemMode if systemMode is not None else "")
        except subprocess.CalledProcessError as e:
            eslog.warning(f"Failed to restore video mode: {e}")
        except Exception as e:
            eslog.warning(f"Unexpected error restoring video mode: {e}")
    if mouseChanged:
        try:
            videoMode.changeMouse(False)
        except subprocess.CalledProcessError as e:
            eslog.warning(f"Failed to restore mouse visibility: {e}")
        except Exception as e:
            eslog.warning(f"Unexpected error restoring mouse visibility: {e}")
    if wheelProcesses:
        try:
            wheelsUtils.resetControllers(wheelProcesses)
        except Exception as e:
            eslog.error(f"Unable to reset wheel controllers: {e}")
            pass


def start_rom(args, maxnbplayers, rom, romConfiguration):
    """
    Prepares the system and launches the emulator for a given ROM.

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
        romConfiguration (str): The ROM file path used for specific configurations.

    Returns:
        int: The exit code from the emulator process.
    """
    # Initial setup
    playersControllers = _configure_controllers(args, maxnbplayers)
    system = _setup_system_emulator(args, romConfiguration)
    metadata = controllers.getGamesMetaData(system.name, rom)
    guns, wheels, wheelProcesses, playersControllers = _configure_special_devices(
        args, system, rom, metadata, playersControllers
    )
    generator = getGenerator(system.config["emulator"])

    exitCode = -1
    resolutionChanged, mouseChanged = False, False
    systemMode = videoMode.getCurrentMode()

    try:
        # Configure video and mouse settings
        systemMode, resolutionChanged, mouseChanged, gameResolution = (
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
        exitCode = _launch_emulator_process(
            generator,
            system,
            rom,
            playersControllers,
            metadata,
            guns,
            wheels,
            gameResolution,
            args,
            romConfiguration,
        )

        # Execute post-launch scripts
        _execute_external_scripts(system, rom, "gameStop")

    finally:
        _cleanup_system(resolutionChanged, systemMode, mouseChanged, wheelProcesses)

    return exitCode


def _cleanup_temp_files(*temp_files):
    """
    Cleans up temporary files created during bezel processing.

    Args:
        *temp_files: Variable number of temporary file paths to cleanup
    """
    import os

    for temp_file in temp_files:
        try:
            if temp_file and path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            eslog.warning(f"Could not remove temporary file {temp_file}: {e}")


def getHudBezel(system, generator, rom, gameResolution, bordersSize):
    """
    Determines and prepares the appropriate bezel image for the HUD.

    It checks for bezel compatibility (aspect ratio, coverage) and resizes,
    tattoos, or adds borders to the image as needed.

    Args:
        system (Emulator): The current system's configuration object.
        generator (Generator): The emulator-specific generator.
        rom (str): Path to the ROM file.
        gameResolution (dict): The current game resolution.
        bordersSize (str): The size of the gun borders, if any.

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
        and bordersSize is None
    ):
        return None

    # List of temporary files that may be created
    temp_files = []

    try:
        # If no bezel is set but effects are needed, create a transparent base.
        if "bezel" not in system.config or system.config["bezel"] in ["", "none"]:
            overlay_png_file = "/tmp/bezel_transhud_black.png"
            overlay_info_file = "/tmp/bezel_transhud_black.info"
            temp_files.extend([overlay_png_file, overlay_info_file])
            bezelsUtil.createTransparentBezel(
                overlay_png_file, gameResolution["width"], gameResolution["height"]
            )

            w, h = gameResolution["width"], gameResolution["height"]
            with open(overlay_info_file, "w") as fd:
                fd.write(
                    f'{{"width":{w}, "height":{h}, "opacity":1.0, "messagex":0.22, "messagey":0.12}}'
                )
        else:
            # A bezel is configured, so let's find its files.
            eslog.debug(
                f"HUD enabled. Trying to apply the bezel {system.config['bezel']}"
            )
            bezel = system.config["bezel"]
            bz_infos = bezelsUtil.getBezelInfos(
                rom, bezel, system.name, system.config["emulator"]
            )
            if bz_infos is None:
                eslog.debug("No bezel info file found")
                return None
            overlay_info_file, overlay_png_file = bz_infos["info"], bz_infos["png"]

        # --- Bezel Validation ---
        infos = {}  # Initialize infos here to ensure it's always defined
        try:
            with open(overlay_info_file) as f:
                infos = json.load(f)
        except FileNotFoundError:
            eslog.warning(f"Bezel info file not found: {overlay_info_file}")
        except json.JSONDecodeError as e:
            eslog.warning(f"Invalid JSON in bezel info file {overlay_info_file}: {e}")
        except Exception as e:
            eslog.warning(f"Unable to read bezel info file {overlay_info_file}: {e}")

        # Get bezel dimensions either from info file or the image itself.
        if "width" in infos and "height" in infos:
            bezel_width, bezel_height = infos["width"], infos["height"]
            eslog.info(f"Bezel size read from {overlay_info_file}")
        else:
            bezel_width, bezel_height = bezelsUtil.fast_image_size(overlay_png_file)
            eslog.info(f"Bezel size read from {overlay_png_file}")

        # Define validation thresholds.
        max_ratio_delta = 0.01  # Max difference between screen and bezel aspect ratio.

        screen_ratio = gameResolution["width"] / gameResolution["height"]
        bezel_ratio = bezel_width / bezel_height

        # Validate aspect ratio (unless gun borders are being added, which might need a different ratio).
        if bordersSize is None and abs(screen_ratio - bezel_ratio) > max_ratio_delta:
            eslog.debug(
                f"Screen ratio ({screen_ratio}) is too far from the bezel one ({bezel_ratio})"
            )
            return None

        # --- Bezel Processing ---
        # Resize the bezel image if it doesn't match the screen resolution.
        bezel_stretch = system.isOptSet("bezel_stretch") and system.getOptBoolean(
            "bezel_stretch"
        )
        if (
            bezel_width != gameResolution["width"]
            or bezel_height != gameResolution["height"]
        ):
            eslog.debug("Bezel needs to be resized")
            output_png_file = "/tmp/bezel.png"
            temp_files.append(output_png_file)
            try:
                bezelsUtil.resizeImage(
                    overlay_png_file,
                    output_png_file,
                    gameResolution["width"],
                    gameResolution["height"],
                    bezel_stretch,
                )
                overlay_png_file = output_png_file
            except Exception as e:
                eslog.error(f"Failed to resize the image: {e}")
                return None

        # Apply a "tattoo" (watermark/logo) to the bezel if configured.
        if system.isOptSet("bezel.tattoo") and system.config["bezel.tattoo"] != "0":
            output_png_file = "/tmp/bezel_tattooed.png"
            temp_files.append(output_png_file)
            bezelsUtil.tatooImage(overlay_png_file, output_png_file, system)
            overlay_png_file = output_png_file

        # Draw gun borders on the bezel if required.
        if bordersSize is not None:
            eslog.debug("Drawing gun borders")
            output_png_file = "/tmp/bezel_gunborders.png"
            temp_files.append(output_png_file)
            innerSize, outerSize = bezelsUtil.gunBordersSize(bordersSize)
            color = bezelsUtil.gunsBordersColorFomConfig(system.config)
            bezelsUtil.gunBorderImage(
                overlay_png_file, output_png_file, innerSize, outerSize, color
            )
            overlay_png_file = output_png_file

        eslog.debug(f"Applying bezel {overlay_png_file}")
        return overlay_png_file

    finally:
        # Clean up temporary files
        _cleanup_temp_files(*temp_files)


def extractGameInfosFromXml(xml):
    """
    Parses a game information XML file to extract game name and thumbnail.

    Args:
        xml (str): Path to the game info XML file.

    Returns:
        dict: A dictionary containing 'name' and 'thumbnail' if found.
    """
    import xml.etree.ElementTree as ET

    vals = {}
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


def callExternalScripts(folder, event, args):
    """
    Executes all executable scripts in a given folder.

    Args:
        folder (str): The directory containing the scripts.
        event (str): The event name (e.g., "gameStart", "gameStop").
        args (list): A list of arguments to pass to the scripts.
    """
    if not path.isdir(folder):
        return
    try:
        file_list = sorted(listdir(folder))  # Sort for predictable execution order.
    except OSError as e:
        eslog.warning(f"Could not read directory {folder}: {e}")
        return

    for file in file_list:
        filepath = path.join(folder, file)
        if path.isdir(filepath):
            callExternalScripts(filepath, event, args)  # Recurse into subdirectories.
        elif access(filepath, X_OK):
            eslog.debug(f"Calling external script: {str([filepath, event] + args)}")
            try:
                result = call([filepath, event] + args)
                if result != 0:
                    eslog.warning(
                        f"External script {filepath} returned non-zero exit code: {result}"
                    )
            except OSError as e:
                eslog.error(f"Failed to execute external script {filepath}: {e}")
            except Exception as e:
                eslog.error(
                    f"Unexpected error executing external script {filepath}: {e}"
                )


def hudConfig_protectStr(text):
    """
    Returns an empty string if the input is None, otherwise returns the input.

    Args:
        text (str): The string to protect.

    Returns:
        str: The original string or an empty string.
    """
    return text or ""


def getHudConfig(system, systemName, emulator, core, rom, gameinfos, bezel):
    """
    Generates the configuration string for MangoHUD.

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
    configstr = configstr.replace("%THUMBNAIL%", hudConfig_protectStr(gameThumbnail))

    return configstr


def runCommand(command):
    """
    Executes a command in a subprocess.

    Args:
        command (Command): A Command object containing the command array and environment variables.

    Returns:
        int: The exit code of the process.
    """
    global proc

    if not command.array:
        return -1

    # Combine current environment with command-specific environment variables.
    envvars = {**environ, **command.env}

    eslog.debug(f"command: {str(command)}")
    eslog.debug(f"command: {str(command.array)}")
    eslog.debug(f"env: {str(envvars)}")
    exitcode = -1

    proc = Popen(command.array, env=envvars, stdout=PIPE, stderr=PIPE)
    try:
        out, err = proc.communicate()
        exitcode = proc.returncode
        # Decode and log stdout/stderr.
        if out:
            eslog.debug(out.decode(errors="ignore"))
        if err:
            eslog.error(err.decode(errors="ignore"))
    except BrokenPipeError:
        # This can happen if the parent process (like `head`) closes the pipe.
        eslog.debug("Broken pipe when communicating with emulator process")
    except OSError as e:
        eslog.error(f"OS error when communicating with emulator process: {e}")
    except Exception as e:
        eslog.error(
            f"Unexpected error when communicating with emulator process: {e}",
            exc_info=True,
        )
    finally:
        # Ensure process resources are properly released
        if proc and proc.poll() is None:  # Process is still running
            try:
                proc.kill()
            except ProcessLookupError:
                # Process already finished, ignore
                pass
        proc = None  # Clear the global reference

    return exitcode


def signal_handler(signal, frame):
    """
    Handles termination signals (like Ctrl+C) to gracefully kill the emulator process.
    """
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
            f"-p{p}index", help=f"player {p} controller index", type=int
        )
        parser.add_argument(
            f"-p{p}guid", help=f"player {p} controller SDL2 guid", type=str
        )
        parser.add_argument(f"-p{p}name", help=f"player {p} controller name", type=str)
        parser.add_argument(
            f"-p{p}devicepath", help=f"player {p} controller device path", type=str
        )
        parser.add_argument(
            f"-p{p}nbbuttons", help=f"player {p} controller number of buttons", type=str
        )
        parser.add_argument(
            f"-p{p}nbhats", help=f"player {p} controller number of hats", type=str
        )
        parser.add_argument(
            f"-p{p}nbaxes", help=f"player {p} controller number of axes", type=str
        )

    # General arguments for system, ROM, and specific features.
    parser.add_argument(
        "-system", help="Select the system to launch", type=str, required=True
    )
    parser.add_argument(
        "-rom", help="Absolute path to the ROM", type=str, required=True
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
        "-state_filename", help="Load state from a specific filename", type=str
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
        "-lightgun", help="Configure for lightgun usage", action="store_true"
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
            profiler.dump_stats("/var/run/emulatorlauncher.prof")
        except Exception as e:
            eslog.error(f"Error dumping profiler stats: {e}")

    # A short delay can help ensure resources (like GPU memory) are fully released before returning to the frontend.
    sleep(1)
    eslog.debug(f"Exiting configgen with status {str(exitcode)}")

    exit(exitcode)
