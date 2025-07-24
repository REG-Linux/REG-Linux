#!/usr/bin/env python3
"""
This script is the emulator launcher for the Reglinux distribution.
It is responsible for preparing the environment and launching the emulator
with the appropriate configurations.
"""

import os
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
if os.path.exists("/var/run/emulatorlauncher.perf"):
    import cProfile
    profiler = cProfile.Profile()
    profiler.enable()

### Always required imports ###
import argparse
import GeneratorImporter
import signal
import time
import subprocess
import systemFiles
import utils.videoMode as videoMode
import utils.gunsUtils as gunsUtils
import utils.wheelsUtils as wheelsUtils
import utils.windowsManager as windowsManager
import utils.bezels as bezelsUtil
import controllers as controllers
import utils.zar as zar
from sys import exit
from Emulator import Emulator

from utils.logger import get_logger
eslog = get_logger(__name__)

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
    # Get the file extension in lowercase
    extension = os.path.splitext(args.rom)[1][1:].lower()

    # Check if it is a .zar archive
    if extension == "zar":
        exitCode = 0
        need_end = False
        rommountpoint = None

        try:
            # Mount the archive and get the actual ROM path
            need_end, rommountpoint, rom = zar.zar_begin(args.rom)

            # Launch the game using the mounted ROM
            exitCode = start_rom(args, maxnbplayers, rom, args.rom)

        finally:
            # Unmount the archive after the game ends
            if need_end and rommountpoint is not None:
                zar.zar_end(rommountpoint)

        return exitCode

    else:
        # If it's not a .zar file, launch the ROM directly
        return start_rom(args, maxnbplayers, args.rom, args.rom)

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
    global profiler

    # --- Controller Configuration ---
    playersControllers = dict()
    controllersInput = []
    # Collect controller information from command-line arguments for each player.
    for p in range(1, maxnbplayers + 1):
        ci = {
            "index":      getattr(args, f"p{p}index"),
            "guid":       getattr(args, f"p{p}guid"),
            "name":       getattr(args, f"p{p}name"),
            "devicepath": getattr(args, f"p{p}devicepath"),
            "nbbuttons":  getattr(args, f"p{p}nbbuttons"),
            "nbhats":     getattr(args, f"p{p}nbhats"),
            "nbaxes":     getattr(args, f"p{p}nbaxes")
        }
        controllersInput.append(ci)

    # Load the controller configurations based on the input.
    playersControllers = controllers.loadControllerConfig(controllersInput)

    # --- System and Emulator Setup ---
    systemName = args.system
    eslog.debug(f"Running system: {systemName}")
    # Initialize the Emulator object, which holds all configuration for the system.
    system = Emulator(systemName, romConfiguration)

    # Override default emulator and core if specified in arguments.
    if args.emulator is not None:
        system.config["emulator"] = args.emulator
        system.config["emulator-forced"] = True
    if args.core is not None:
        system.config["core"] = args.core
        system.config["core-forced"] = True

    # For logging purposes, create a copy of the config and hide sensitive data.
    debugDisplay = system.config.copy()
    if "retroachievements.password" in debugDisplay:
        debugDisplay["retroachievements.password"] = "***"
    eslog.debug(f"Settings: {debugDisplay}")

    if "emulator" in system.config:
        core_info = f", core: {system.config['core']}" if "core" in system.config else ""
        eslog.debug(f"emulator: {system.config['emulator']}{core_info}")

    # --- Metadata and Device Handling ---
    metadata = controllers.getGamesMetaData(systemName, rom)

    # Configure light guns if enabled for the game.
    if not system.isOptSet('use_guns') and args.lightgun:
        system.config["use_guns"] = True
    if system.isOptSet('use_guns') and system.getOptBoolean('use_guns'):
        guns = controllers.getGuns()
        core = system.config.get("core")
        gunsUtils.precalibration(systemName, system.config['emulator'], core, rom)
    else:
        eslog.info("Guns disabled.")
        guns = []

    # Configure racing wheels if enabled for the game.
    wheelProcesses = None
    if not system.isOptSet('use_wheels') and args.wheel:
        system.config["use_wheels"] = True
    if system.isOptSet('use_wheels') and system.getOptBoolean('use_wheels'):
        deviceInfos = controllers.getDevicesInformation()
        (wheelProcesses, playersControllers, deviceInfos) = wheelsUtils.reconfigureControllers(playersControllers, system, rom, metadata, deviceInfos)
        wheels = wheelsUtils.getWheelsFromDevicesInfos(deviceInfos)
    else:
        eslog.info("Wheels disabled.")
        wheels = []

    # --- Generator and Video Mode ---
    # The "generator" is responsible for creating the emulator command line.
    generator = GeneratorImporter.getGenerator(system.config['emulator'])

    # Determine the desired video mode for the game.
    wantedGameMode = generator.getResolutionMode(system.config)
    systemMode = videoMode.getCurrentMode()

    resolutionChanged = False
    mouseChanged = False
    exitCode = -1
    try:
        # If videomode is 'auto' or 'default', switch to a minimal resolution to save resources.
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

        # Change the video mode if the game requires a specific one.
        if wantedGameMode != 'default' and wantedGameMode != newsystemMode:
            videoMode.changeMode(wantedGameMode)
            resolutionChanged = True
        gameResolution = videoMode.getCurrentResolution()

        # Create save directory for the system if it doesn't exist.
        dirname = os.path.join(systemFiles.SAVES, system.name)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # --- Argument and Option Finalization ---
        effectiveCore = system.config.get("core", "")
        effectiveRom = rom or ""

        # Apply netplay options from arguments.
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

        # Apply save state options from arguments.
        if args.state_slot is not None:
            system.config["state_slot"] = args.state_slot
        if args.autosave is not None:
            system.config["autosave"] = args.autosave
        if args.state_filename is not None:
            system.config["state_filename"] = args.state_filename

        # Show/hide mouse cursor based on generator's requirement.
        if generator.getMouseMode(system.config, rom):
            mouseChanged = True
            videoMode.changeMouse(True)

        # Configure SDL_RENDER_VSYNC based on system settings.
        system.config["sdlvsync"] = '0' if system.isOptSet('sdlvsync') and not system.getOptBoolean('sdlvsync') else '1'
        os.environ['SDL_RENDER_VSYNC'] = system.config["sdlvsync"]

        # --- Script Execution and Emulator Launch ---
        # Execute custom scripts before the emulator starts.
        callExternalScripts("/usr/share/reglinux/configgen/scripts", "gameStart", [systemName, system.config['emulator'], effectiveCore, effectiveRom])
        callExternalScripts("/userdata/system/scripts", "gameStart", [systemName, system.config['emulator'], effectiveCore, effectiveRom])

        eslog.debug("==== Running emulator ====")
        try:
            # Start a window compositor like Wayland or X11 if required by the emulator.
            if generator.requiresWayland() or generator.requiresX11():
                if 'WAYLAND_DISPLAY' not in os.environ:
                    windowsManager.start_compositor(generator, system)

            # Change the execution directory if required by the generator.
            executionDirectory = generator.executionDirectory(system.config, effectiveRom)
            if executionDirectory is not None:
                os.chdir(executionDirectory)

            # Generate the final command to run the emulator.
            cmd = generator.generate(system, rom, playersControllers, metadata, guns, wheels, gameResolution)

            # Configure and enable MangoHUD if supported and enabled.
            if system.isOptSet('hud_support') and os.path.exists("/usr/bin/mangohud") and system.getOptBoolean('hud_support'):
                hud_bezel = getHudBezel(system, generator, rom, gameResolution, controllers.gunsBordersSizeName(guns, system.config))
                if (system.isOptSet('hud') and system.config['hud'] not in ["", "none"]) or hud_bezel is not None:
                    gameinfos = extractGameInfosFromXml(args.gameinfoxml)
                    cmd.env["MANGOHUD_DLSYM"] = "1"
                    hudconfig = getHudConfig(system, args.systemname, system.config['emulator'], effectiveCore, rom, gameinfos, hud_bezel)
                    with open('/var/run/hud.config', 'w') as f:
                        f.write(hudconfig)
                    cmd.env["MANGOHUD_CONFIGFILE"] = "/var/run/hud.config"
                    if not generator.hasInternalMangoHUDCall():
                        cmd.array.insert(0, "mangohud")

            # Disable profiler during command execution to focus on the script's own performance.
            if profiler:
                profiler.disable()
            exitCode = runCommand(cmd)
            if profiler:
                profiler.enable()
        finally:
            # Stop the compositor after the emulator exits.
            if generator.requiresWayland() or generator.requiresX11():
                windowsManager.stop_compositor(generator, system)

        # Execute custom scripts after the emulator stops.
        callExternalScripts("/userdata/system/scripts", "gameStop", [systemName, system.config['emulator'], effectiveCore, effectiveRom])
        callExternalScripts("/usr/share/reglinux/configgen/scripts", "gameStop", [systemName, system.config['emulator'], effectiveCore, effectiveRom])

    finally:
        # --- Cleanup ---
        # Always restore the original video mode.
        if resolutionChanged:
            try:
                videoMode.changeMode(systemMode if systemMode is not None else "")
            except Exception:
                pass  # Don't let cleanup failures prevent exit.

        # Restore mouse cursor visibility.
        if mouseChanged:
            try:
                videoMode.changeMouse(False)
            except Exception:
                pass

        # Reset wheel controller configurations.
        if wheelProcesses:
            try:
                wheelsUtils.resetControllers(wheelProcesses)
            except Exception:
                eslog.error("Unable to reset wheel controllers!")
                pass

    return exitCode

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
    # Skip if the emulator handles its own bezels.
    if generator.supportsInternalBezels():
        eslog.debug(f"Skipping bezels for emulator {system.config['emulator']}")
        return None
    # Skip if no bezel is configured and no special effects (tattoo, borders) are needed.
    if ('bezel' not in system.config or system.config['bezel'] in ["", "none"]) and \
       not (system.isOptSet('bezel.tattoo') and system.config['bezel.tattoo'] != "0") and \
       bordersSize is None:
        return None

    # If no bezel is set but effects are needed, create a transparent base.
    if ('bezel' not in system.config or system.config['bezel'] in ["", "none"]):
        overlay_png_file  = "/tmp/bezel_transhud_black.png"
        overlay_info_file = "/tmp/bezel_transhud_black.info"
        bezelsUtil.createTransparentBezel(overlay_png_file, gameResolution["width"], gameResolution["height"])

        w, h = gameResolution["width"], gameResolution["height"]
        with open(overlay_info_file, "w") as fd:
            fd.write(f'{{"width":{w}, "height":{h}, "opacity":1.0, "messagex":0.22, "messagey":0.12}}')
    else:
        # A bezel is configured, so let's find its files.
        eslog.debug(f"HUD enabled. Trying to apply the bezel {system.config['bezel']}")
        bezel = system.config['bezel']
        bz_infos = bezelsUtil.getBezelInfos(rom, bezel, system.name, system.config['emulator'])
        if bz_infos is None:
            eslog.debug("No bezel info file found")
            return None
        overlay_info_file, overlay_png_file = bz_infos["info"], bz_infos["png"]

    # --- Bezel Validation ---
    try:
        import json
        with open(overlay_info_file) as f:
            infos = json.load(f)
    except Exception:
        eslog.warning(f"Unable to read bezel info file: {overlay_info_file}")
        infos = {}

    # Get bezel dimensions either from info file or the image itself.
    if "width" in infos and "height" in infos:
        bezel_width, bezel_height = infos["width"], infos["height"]
        eslog.info(f"Bezel size read from {overlay_info_file}")
    else:
        bezel_width, bezel_height = bezelsUtil.fast_image_size(overlay_png_file)
        eslog.info(f"Bezel size read from {overlay_png_file}")

    # Define validation thresholds.
    max_cover = 0.05  # 5% max coverage of the game area.
    max_ratio_delta = 0.01 # Max difference between screen and bezel aspect ratio.

    screen_ratio = gameResolution["width"] / gameResolution["height"]
    bezel_ratio  = bezel_width / bezel_height

    # Validate aspect ratio (unless gun borders are being added, which might need a different ratio).
    if bordersSize is None and abs(screen_ratio - bezel_ratio) > max_ratio_delta:
        eslog.debug(f"Screen ratio ({screen_ratio}) is too far from the bezel one ({bezel_ratio})")
        return None

    # --- Bezel Processing ---
    # Resize the bezel image if it doesn't match the screen resolution.
    bezel_stretch = system.isOptSet('bezel_stretch') and system.getOptBoolean('bezel_stretch')
    if (bezel_width != gameResolution["width"] or bezel_height != gameResolution["height"]):
        eslog.debug("Bezel needs to be resized")
        output_png_file = "/tmp/bezel.png"
        try:
            bezelsUtil.resizeImage(overlay_png_file, output_png_file, gameResolution["width"], gameResolution["height"], bezel_stretch)
            overlay_png_file = output_png_file
        except Exception as e:
            eslog.error(f"Failed to resize the image: {e}")
            return None

    # Apply a "tattoo" (watermark/logo) to the bezel if configured.
    if system.isOptSet('bezel.tattoo') and system.config['bezel.tattoo'] != "0":
        output_png_file = "/tmp/bezel_tattooed.png"
        bezelsUtil.tatooImage(overlay_png_file, output_png_file, system)
        overlay_png_file = output_png_file

    # Draw gun borders on the bezel if required.
    if bordersSize is not None:
        eslog.debug("Drawing gun borders")
        output_png_file = "/tmp/bezel_gunborders.png"
        innerSize, outerSize = bezelsUtil.gunBordersSize(bordersSize)
        color = bezelsUtil.gunsBordersColorFomConfig(system.config)
        bezelsUtil.gunBorderImage(overlay_png_file, output_png_file, innerSize, outerSize, color)
        overlay_png_file = output_png_file

    eslog.debug(f"Applying bezel {overlay_png_file}")
    return overlay_png_file


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
        infos = ET.parse(xml)
        name_elem = infos.find("./game/name")
        if name_elem is not None:
            vals["name"] = name_elem.text
        thumbnail_elem = infos.find("./game/thumbnail")
        if thumbnail_elem is not None:
            vals["thumbnail"] = thumbnail_elem.text
    except Exception:
        pass # Ignore parsing errors.
    return vals

def callExternalScripts(folder, event, args):
    """
    Executes all executable scripts in a given folder.

    Args:
        folder (str): The directory containing the scripts.
        event (str): The event name (e.g., "gameStart", "gameStop").
        args (list): A list of arguments to pass to the scripts.
    """
    if not os.path.isdir(folder):
        return
    for file in sorted(os.listdir(folder)): # Sort for predictable execution order.
        filepath = os.path.join(folder, file)
        if os.path.isdir(filepath):
            callExternalScripts(filepath, event, args) # Recurse into subdirectories.
        elif os.access(filepath, os.X_OK):
            eslog.debug(f"Calling external script: {str([filepath, event] + args)}")
            subprocess.call([filepath, event] + args)

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
        configstr = f"background_image={hudConfig_protectStr(bezel)}\nlegacy_layout=false\n"

    # If HUD is disabled, just make the background transparent.
    if not system.isOptSet('hud') or system.config['hud'] == "none":
        return configstr + "background_alpha=0\n"

    mode = system.config["hud"]
    # Determine HUD position from config.
    position_map = {"NW": "top-left", "NE": "top-right", "SE": "bottom-right"}
    hud_corner = system.config.get('hud_corner', "")
    hud_position = position_map.get(hud_corner, "bottom-left")

    emulatorstr = f"{emulator}/{core}" if emulator != core and core else emulator
    gameName = gameinfos.get("name", "")
    gameThumbnail = gameinfos.get("thumbnail", "")

    # Apply predefined or custom HUD configurations.
    if mode == "perf":
        configstr += f"position={hud_position}\nbackground_alpha=0.9\nlegacy_layout=false\n" \
                     "custom_text=%GAMENAME%\ncustom_text=%SYSTEMNAME%\ncustom_text=%EMULATORCORE%\n" \
                     "fps\ngpu_name\nengine_version\nvulkan_driver\nresolution\nram\n" \
                     "gpu_stats\ngpu_temp\ncpu_stats\ncpu_temp\ncore_load"
    elif mode == "game":
        configstr += f"position={hud_position}\nbackground_alpha=0\nlegacy_layout=false\n" \
                     "font_size=32\nimage_max_width=200\nimage=%THUMBNAIL%\n" \
                     "custom_text=%GAMENAME%\ncustom_text=%SYSTEMNAME%\ncustom_text=%EMULATORCORE%"
    elif mode == "custom" and system.isOptSet('hud_custom') and system.config["hud_custom"]:
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
    envvars = {**os.environ, **command.env}

    eslog.debug(f"command: {str(command)}")
    eslog.debug(f"command: {str(command.array)}")
    eslog.debug(f"env: {str(envvars)}")
    exitcode = -1

    proc = subprocess.Popen(command.array, env=envvars, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        out, err = proc.communicate()
        exitcode = proc.returncode
        # Decode and log stdout/stderr.
        if out: eslog.debug(out.decode(errors='ignore'))
        if err: eslog.error(err.decode(errors='ignore'))
    except BrokenPipeError:
        # This can happen if the parent process (like `head`) closes the pipe.
        pass
    except Exception:
        eslog.error("Emulator exited unexpectedly", exc_info=True)

    return exitcode

def signal_handler(signal, frame):
    """
    Handles termination signals (like Ctrl+C) to gracefully kill the emulator process.
    """
    global proc
    eslog.debug('Exiting due to signal')
    if proc:
        eslog.debug('Killing emulator process')
        proc.kill()
    exit(0)

if __name__ == '__main__':
    # Register signal handler for graceful termination.
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # --- Argument Parsing ---
    parser = argparse.ArgumentParser(description='Emulator Launcher Script')

    maxnbplayers = 8
    # Dynamically create arguments for each player's controller.
    for p in range(1, maxnbplayers + 1):
        parser.add_argument(f"-p{p}index",      help=f"player {p} controller index",             type=int)
        parser.add_argument(f"-p{p}guid",       help=f"player {p} controller SDL2 guid",         type=str)
        parser.add_argument(f"-p{p}name",       help=f"player {p} controller name",              type=str)
        parser.add_argument(f"-p{p}devicepath", help=f"player {p} controller device path",       type=str)
        parser.add_argument(f"-p{p}nbbuttons",  help=f"player {p} controller number of buttons", type=str)
        parser.add_argument(f"-p{p}nbhats",     help=f"player {p} controller number of hats",    type=str)
        parser.add_argument(f"-p{p}nbaxes",     help=f"player {p} controller number of axes",    type=str)

    # General arguments for system, ROM, and specific features.
    parser.add_argument("-system",         help="Select the system to launch",          type=str, required=True)
    parser.add_argument("-rom",            help="Absolute path to the ROM",             type=str, required=True)
    parser.add_argument("-emulator",       help="Force a specific emulator",            type=str)
    parser.add_argument("-core",           help="Force a specific emulator core",       type=str)
    parser.add_argument("-netplaymode",    help="Netplay mode (host/client)",           type=str)
    parser.add_argument("-netplaypass",    help="Netplay spectator password",           type=str)
    parser.add_argument("-netplayip",      help="Netplay remote IP address",            type=str)
    parser.add_argument("-netplayport",    help="Netplay remote port",                  type=str)
    parser.add_argument("-netplaysession", help="Netplay session identifier",           type=str)
    parser.add_argument("-state_slot",     help="Load state from a specific slot",      type=str)
    parser.add_argument("-state_filename", help="Load state from a specific filename",  type=str)
    parser.add_argument("-autosave",       help="Enable/disable autosave feature",      type=str)
    parser.add_argument("-systemname",     help="System's display name",                type=str)
    parser.add_argument("-gameinfoxml",    help="Path to game info XML metadata",       type=str, nargs='?', default='/dev/null')
    parser.add_argument("-lightgun",       help="Configure for lightgun usage",         action="store_true")
    parser.add_argument("-wheel",          help="Configure for wheel usage",            action="store_true")

    args = parser.parse_args()
    exitcode = -1
    try:
        # Call the main function with parsed arguments.
        exitcode = main(args, maxnbplayers)
    except Exception as e:
        eslog.error("An unhandled exception occurred in configgen:", exc_info=True)

    # --- Finalization ---
    # If profiling was enabled, save the results.
    if profiler:
        profiler.disable()
        profiler.dump_stats('/var/run/emulatorlauncher.prof')

    # A short delay can help ensure resources (like GPU memory) are fully released before returning to the frontend.
    time.sleep(1)
    eslog.debug(f"Exiting configgen with status {str(exitcode)}")

    exit(exitcode)
