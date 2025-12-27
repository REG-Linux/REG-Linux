import builtins
from configparser import ConfigParser
from os import listdir, makedirs, path, remove, rename
from re import search
from shutil import copy2, copyfile
from typing import Any

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config, gunsNeedCrosses
from configgen.generators.Generator import Generator
from configgen.systemFiles import CONF
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

SUPERMODEL_CONFIG_DIR = CONF + "/supermodel"
SUPERMODEL_CONFIG_PATH = SUPERMODEL_CONFIG_DIR + "/Supermodel.ini"
SUPERMODEL_BIN_PATH = "/usr/bin/supermodel"


class SupermodelGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        command_array = [SUPERMODEL_BIN_PATH, "-fullscreen", "-channels=2"]

        # legacy3d
        if system.isOptSet("engine3D") and system.config["engine3D"] == "new3d":
            command_array.append("-new3d")
        else:
            command_array.extend(["-multi-texture", "-legacy-scsp", "-legacy3d"])

        # widescreen
        if system.isOptSet("wideScreen") and system.getOptBoolean("wideScreen"):
            command_array.append("-wide-screen")
            command_array.append("-wide-bg")

        # quad rendering
        if system.isOptSet("quadRendering") and system.getOptBoolean("quadRendering"):
            command_array.append("-quad-rendering")

        # crosshairs
        if system.isOptSet("crosshairs"):
            command_array.append("-crosshairs={}".format(system.config["crosshairs"]))
        else:
            # Check if guns is a dictionary (has guns) or a list (empty list if no guns)
            # If it's an empty list, treat it like an empty dict (no guns, so enable crosses for other devices)
            if isinstance(guns, dict) and gunsNeedCrosses(guns):
                if len(guns) == 1:
                    command_array.append("-crosshairs={}".format("1"))
                else:
                    command_array.append("-crosshairs={}".format("3"))
            elif isinstance(guns, list) and len(guns) == 0:
                # Empty list means no guns, so enable crosses for other input devices (like joysticks, mouses...)
                command_array.append("-crosshairs={}".format("1"))

        # force feedback
        if system.isOptSet("forceFeedback") and system.getOptBoolean("forceFeedback"):
            command_array.append("-force-feedback")

        # powerpc frequesncy
        if system.isOptSet("ppcFreq"):
            command_array.append("-ppc-frequency={}".format(system.config["ppcFreq"]))

        # resolution
        command_array.append(
            "-res={},{}".format(game_resolution["width"], game_resolution["height"])
        )

        # logs
        command_array.extend(["-log-output=/userdata/system/logs/Supermodel.log", rom])

        # copy nvram files
        copy_nvram_files()

        # copy gun asset files
        copy_asset_files()

        # copy xml
        copy_xml()

        # FIXME: configPadsIni is not used in the original code, but it is called here.
        # configPadsIni(system, rom, players_controllers, guns, drivingGame, sensitivity)

        return Command(
            array=command_array,
            env={
                "SDL_VIDEODRIVER": "x11",
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                ),
            },
        )


def copy_nvram_files():
    sourceDir = "/usr/share/supermodel/NVRAM"
    targetDir = "/userdata/saves/supermodel/NVRAM"
    if not path.exists(targetDir):
        makedirs(targetDir)

    # create nv files which are in source and have a newer modification time than in target
    for file in listdir(sourceDir):
        extension = path.splitext(file)[1][1:]
        if extension == "nv":
            sourceFile = path.join(sourceDir, file)
            targetFile = path.join(targetDir, file)
            if not path.exists(targetFile):
                # if the target file doesn't exist, just copy the source file
                copyfile(sourceFile, targetFile)
            else:
                # if the target file exists and has an older modification time than the source file, create a backup and copy the new file
                if path.getmtime(sourceFile) > path.getmtime(targetFile):
                    backupFile = targetFile + ".bak"
                    if path.exists(backupFile):
                        remove(backupFile)
                    rename(targetFile, backupFile)
                    copyfile(sourceFile, targetFile)


def copy_asset_files():
    sourceDir = "/usr/share/supermodel/Assets"
    targetDir = "/userdata/system/configs/supermodel/Assets"
    if not path.exists(sourceDir):
        return
    if not path.exists(targetDir):
        makedirs(targetDir)

    # create asset files which are in source and have a newer modification time than in target
    for file in listdir(sourceDir):
        sourceFile = path.join(sourceDir, file)
        targetFile = path.join(targetDir, file)
        if not path.exists(targetFile) or path.getmtime(sourceFile) > path.getmtime(
            targetFile
        ):
            copyfile(sourceFile, targetFile)


def copy_xml():
    source_path = "/usr/share/supermodel/Games.xml"
    dest_path = "/userdata/system/configs/supermodel/Games.xml"
    if not path.exists(SUPERMODEL_CONFIG_DIR):
        makedirs(SUPERMODEL_CONFIG_DIR)
    if not path.exists(dest_path) or path.getmtime(source_path) > path.getmtime(
        dest_path
    ):
        copy2(source_path, dest_path)


def configPadsIni(
    system: Any,
    rom: str,
    players_controllers: Any,
    guns: Any,
    altControl: Any,
    sensitivity: Any,
) -> tuple[str, dict[str, str | None]]:
    # Reduce cyclomatic complexity by splitting logic into helper functions

    def get_template_and_mapping(altControl: Any) -> tuple[str, dict[str, str | None]]:
        if bool(altControl):
            templateFile = "/usr/share/supermodel/Supermodel-Driving.ini.template"
            mapping = {
                "button1": "y",
                "button2": "b",
                "button3": "a",
                "button4": "x",
                "button5": "pageup",
                "button6": "pagedown",
                "button7": None,
                "button8": None,
                "button9": "start",  # start
                "button10": "select",  # coins
                "axisX": "joystick1left",
                "axisY": "joystick1up",
                "axisZ": "l2",
                "axisRX": "joystick2left",
                "axisRY": "joystick2up",
                "axisRZ": "r2",
                "left": "joystick1left",
                "right": "joystick1right",
                "up": "joystick1up",
                "down": "joystick1down",
            }
        else:
            templateFile = "/usr/share/supermodel/Supermodel.ini.template"
            mapping = {
                "button1": "y",
                "button2": "b",
                "button3": "a",
                "button4": "x",
                "button5": "pageup",
                "button6": "pagedown",
                "button7": "l2",
                "button8": "r2",
                "button9": "start",  # start
                "button10": "select",  # coins
                "axisX": "joystick1left",
                "axisY": "joystick1up",
                "axisZ": None,
                "axisRX": "joystick2left",
                "axisRY": "joystick2up",
                "axisRZ": None,
                "left": "joystick1left",
                "right": "joystick1right",
                "up": "joystick1up",
                "down": "joystick1down",
            }
        return templateFile, mapping

    # Call to the internal function
    templateFile, mapping = get_template_and_mapping(altControl)

    def apply_guns_to_section(
        targetConfig: Any,
        section: str,
        key: str,
        value: str,
        system: Any,
        guns: Any,
        players_controllers: Any,
        mapping: Any,
        mapping_fallback: Any,
    ) -> bool:
        # Returns True if handled, False otherwise
        if (
            system.isOptSet("use_guns")
            and system.getOptBoolean("use_guns")
            and len(guns) >= 1
        ):
            if key == "InputSystem":
                targetConfig.set(section, key, "evdev")
                return True
            if key == "InputAnalogJoyX":
                targetConfig.set(section, key, "MOUSE1_XAXIS_INV")
                return True
            if key == "InputAnalogJoyY":
                targetConfig.set(section, key, "MOUSE1_YAXIS_INV")
                return True
            if key == "InputGunX" or key == "InputAnalogGunX":
                targetConfig.set(section, key, "MOUSE1_XAXIS")
                return True
            if key == "InputGunY" or key == "InputAnalogGunY":
                targetConfig.set(section, key, "MOUSE1_YAXIS")
                return True
            if (
                key == "InputTrigger"
                or key == "InputAnalogTriggerLeft"
                or key == "InputAnalogJoyTrigger"
            ):
                targetConfig.set(section, key, "MOUSE1_LEFT_BUTTON")
                return True
            if key == "InputOffscreen" or key == "InputAnalogTriggerRight":
                targetConfig.set(section, key, "MOUSE1_RIGHT_BUTTON")
                return True
            if key == "InputStart1":
                val = transformElement(
                    "JOY1_BUTTON9", players_controllers, mapping, mapping_fallback
                )
                val = "," + val if val is not None else ""
                targetConfig.set(section, key, "MOUSE1_BUTTONX1" + val)
                return True
            if key == "InputCoin1":
                val = transformElement(
                    "JOY1_BUTTON10", players_controllers, mapping, mapping_fallback
                )
                val = "," + val if val is not None else ""
                targetConfig.set(section, key, "MOUSE1_BUTTONX2" + val)
                return True
            if key == "InputAnalogJoyEvent":
                val = transformElement(
                    "JOY1_BUTTON2", players_controllers, mapping, mapping_fallback
                )
                val = "," + val if val is not None else ""
                targetConfig.set(section, key, "KEY_S,MOUSE1_MIDDLE_BUTTON" + val)
                return True
            if len(guns) >= 2:
                if key == "InputAnalogJoyX2":
                    targetConfig.set(section, key, "MOUSE2_XAXIS_INV")
                    return True
                if key == "InputAnalogJoyY2":
                    targetConfig.set(section, key, "MOUSE2_YAXIS_INV")
                    return True
                if key == "InputGunX2" or key == "InputAnalogGunX2":
                    targetConfig.set(section, key, "MOUSE2_XAXIS")
                    return True
                if key == "InputGunY2" or key == "InputAnalogGunY2":
                    targetConfig.set(section, key, "MOUSE2_YAXIS")
                    return True
                if (
                    key == "InputTrigger2"
                    or key == "InputAnalogTriggerLeft2"
                    or key == "InputAnalogJoyTrigger2"
                ):
                    targetConfig.set(section, key, "MOUSE2_LEFT_BUTTON")
                    return True
                if key == "InputOffscreen2" or key == "InputAnalogTriggerRight2":
                    targetConfig.set(section, key, "MOUSE2_RIGHT_BUTTON")
                    return True
                if key == "InputStart2":
                    val = transformElement(
                        "JOY2_BUTTON9", players_controllers, mapping, mapping_fallback
                    )
                    val = val + "," + val if val is not None else ""
                    targetConfig.set(section, key, "MOUSE2_BUTTONX1" + val)
                    return True
                if key == "InputCoin1":
                    val = transformElement(
                        "JOY2_BUTTON10", players_controllers, mapping, mapping_fallback
                    )
                    val = val + "," + val if val is not None else ""
                    targetConfig.set(section, key, "MOUSE2_BUTTONX2" + val)
                    return True
                if key == "InputAnalogJoyEvent2":
                    val = transformElement(
                        "JOY2_BUTTON2", players_controllers, mapping, mapping_fallback
                    )
                    val = val + "," + val if val is not None else ""
                    targetConfig.set(section, key, "MOUSE2_MIDDLE_BUTTON" + val)
                    return True
        return False

    templateFile, mapping = get_template_and_mapping(altControl)
    targetFile = SUPERMODEL_CONFIG_PATH

    mapping_fallback = {
        "axisX": "left",
        "axisY": "up",
        "right": "right",
        "down": "down",
        "left": "left",
        "up": "up",
    }

    # template
    templateConfig = ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    templateConfig.optionxform = lambda optionstr: str(optionstr)
    # Fix: Use read_file instead of deprecated readfp
    with builtins.open(templateFile, encoding="utf_8_sig") as fp:
        templateConfig.read_file(fp)

    # target
    targetConfig = ConfigParser(interpolation=None)
    # To prevent ConfigParser from converting to lower case
    targetConfig.optionxform = lambda optionstr: str(optionstr)

    for section in templateConfig.sections():
        targetConfig.add_section(section)
        for key, value in templateConfig.items(section):
            targetConfig.set(
                section,
                key,
                transformValue(value, players_controllers, mapping, mapping_fallback),
            )

    # apply guns
    romBase = path.splitext(path.basename(rom))[0]  # filename without extension
    for section in targetConfig.sections():
        if section.strip() in ["Global", romBase]:
            # for an input system
            if section.strip() != "Global":
                targetConfig.set(section, "InputSystem", "to be defined")
            for key, value in targetConfig.items(section):
                handled = apply_guns_to_section(
                    targetConfig,
                    section,
                    key,
                    value,
                    system,
                    guns,
                    players_controllers,
                    mapping,
                    mapping_fallback,
                )
                if not handled and key == "InputSystem":
                    targetConfig.set(section, key, "sdl")

    # Update InputJoy1XSaturation key with the given sensitivity value
    sensitivity = str(int(float(sensitivity)))
    for section in targetConfig.sections():
        if targetConfig.has_option(section, "InputJoy1XSaturation"):
            targetConfig.set(section, "InputJoy1XSaturation", sensitivity)

    # save the ini file
    if not path.exists(path.dirname(targetFile)):
        makedirs(path.dirname(targetFile))
    with builtins.open(targetFile, "w") as configfile:
        targetConfig.write(configfile)

    return templateFile, mapping


def transformValue(
    value: str, players_controllers: Any, mapping: Any, mapping_fallback: Any
) -> str:
    # remove comments
    cleanValue = value
    matches = search("^([^;]*[^ ])[ ]*;.*$", value)
    if matches:
        cleanValue = matches.group(1)

    if cleanValue[0] == '"' and cleanValue[-1] == '"':
        newvalue = ""
        for elt in cleanValue[1:-1].split(","):
            newelt = transformElement(
                elt, players_controllers, mapping, mapping_fallback
            )
            if newelt is not None:
                if newvalue != "":
                    newvalue = newvalue + ","
                newvalue = newvalue + newelt
        return '"' + newvalue + '"'
    # integers
    return cleanValue


def transformElement(
    elt: str, players_controllers: Any, mapping: Any, mapping_fallback: Any
) -> str | None:
    # Docs/README.txt
    # JOY1_LEFT  is the same as JOY1_XAXIS_NEG
    # JOY1_RIGHT is the same as JOY1_XAXIS_POS
    # JOY1_UP    is the same as JOY1_YAXIS_NEG
    # JOY1_DOWN  is the same as JOY1_YAXIS_POS

    matches = search("^JOY([12])_BUTTON([0-9]*)$", elt)
    if matches:
        return input2input(
            players_controllers,
            matches.group(1),
            joy2realjoyid(players_controllers, matches.group(1)),
            mapping["button" + matches.group(2)],
        )
    matches = search("^JOY([12])_UP$", elt)
    if matches:
        # check joystick type if it's hat or axis
        joy_type = hatOrAxis(players_controllers, matches.group(1))
        key_up = "up" if joy_type == "hat" else "axisY"
        mp = getMappingKeyIncludingFallback(
            players_controllers, matches.group(1), key_up, mapping, mapping_fallback
        )
        eslog.debug(mp)
        return input2input(
            players_controllers,
            matches.group(1),
            joy2realjoyid(players_controllers, matches.group(1)),
            mp,
            -1,
        )
    matches = search("^JOY([12])_DOWN$", elt)
    if matches:
        joy_type = hatOrAxis(players_controllers, matches.group(1))
        key_down = "down" if joy_type == "hat" else "axisY"
        mp = getMappingKeyIncludingFallback(
            players_controllers, matches.group(1), key_down, mapping, mapping_fallback
        )
        return input2input(
            players_controllers,
            matches.group(1),
            joy2realjoyid(players_controllers, matches.group(1)),
            mp,
            1,
        )
    matches = search("^JOY([12])_LEFT$", elt)
    if matches:
        joy_type = hatOrAxis(players_controllers, matches.group(1))
        key_left = "left" if joy_type == "hat" else "axisX"
        mp = getMappingKeyIncludingFallback(
            players_controllers, matches.group(1), key_left, mapping, mapping_fallback
        )
        return input2input(
            players_controllers,
            matches.group(1),
            joy2realjoyid(players_controllers, matches.group(1)),
            mp,
            -1,
        )
    matches = search("^JOY([12])_RIGHT$", elt)
    if matches:
        joy_type = hatOrAxis(players_controllers, matches.group(1))
        key_right = "right" if joy_type == "hat" else "axisX"
        mp = getMappingKeyIncludingFallback(
            players_controllers, matches.group(1), key_right, mapping, mapping_fallback
        )
        return input2input(
            players_controllers,
            matches.group(1),
            joy2realjoyid(players_controllers, matches.group(1)),
            mp,
            1,
        )

    matches = search("^JOY([12])_(R?[XY])AXIS$", elt)
    if matches:
        return input2input(
            players_controllers,
            matches.group(1),
            joy2realjoyid(players_controllers, matches.group(1)),
            mapping["axis" + matches.group(2)],
        )
    matches = search("^JOY([12])_(R?[XYZ])AXIS_NEG$", elt)
    if matches:
        return input2input(
            players_controllers,
            matches.group(1),
            joy2realjoyid(players_controllers, matches.group(1)),
            mapping["axis" + matches.group(2)],
            -1,
        )
    matches = search("^JOY([12])_(R?[XYZ])AXIS_POS$", elt)
    if matches:
        return input2input(
            players_controllers,
            matches.group(1),
            joy2realjoyid(players_controllers, matches.group(1)),
            mapping["axis" + matches.group(2)],
            1,
        )
    if matches:
        return None
    return elt


def getMappingKeyIncludingFallback(
    players_controllers: Any,
    padnum: int | str,
    key: str,
    mapping: Any,
    mapping_fallback: Any,
) -> str:
    if (
        padnum in players_controllers
        and (
            key not in mapping
            or (
                key in mapping
                and mapping[key] not in players_controllers[padnum].inputs
            )
        )
        and (
            key in mapping_fallback
            and mapping_fallback[key] in players_controllers[padnum].inputs
        )
    ):
        return mapping_fallback[key]
    return mapping[key]


def joy2realjoyid(players_controllers: Any, joy: str | int) -> int | None:
    if joy in players_controllers:
        return players_controllers[joy].index
    return None


def hatOrAxis(players_controllers: Any, player: str | int) -> str:
    # default to axis
    type = "axis"
    if (player) in players_controllers:
        pad = players_controllers[(player)]
        for button in pad.inputs:
            input = pad.inputs[button]
            if input.type == "hat":
                type = "hat"
            elif input.type == "axis":
                type = "axis"
    return type


def input2input(
    players_controllers: Any,
    player: str | int,
    joynum: int | None,
    button: str,
    axisside: int | str | None = None,
) -> str | None:
    if (player) in players_controllers:
        pad = players_controllers[(player)]
        if button in pad.inputs:
            input = pad.inputs[button]
            if joynum is not None:  # Only proceeds if joynum is not None
                if input.type == "button":
                    return f"JOY{joynum + 1}_BUTTON{int(input.id) + 1}"
                if input.type == "hat":
                    if input.value == "1":
                        return f"JOY{joynum + 1}_UP,JOY{joynum + 1}_POV1_UP"
                    if input.value == "2":
                        return f"JOY{joynum + 1}_RIGHT,JOY{joynum + 1}_POV1_RIGHT"
                    if input.value == "4":
                        return f"JOY{joynum + 1}_DOWN,JOY{joynum + 1}_POV1_DOWN"
                    if input.value == "8":
                        return f"JOY{joynum + 1}_LEFT,JOY{joynum + 1}_POV1_LEFT"
                elif input.type == "axis":
                    sidestr = ""
                    if axisside is not None:
                        if axisside == 1:
                            sidestr = "_NEG" if input.value == 1 else "_POS"
                        else:
                            sidestr = "_POS" if input.value == 1 else "_NEG"

                    if button == "joystick1left" or button == "left":
                        return f"JOY{joynum + 1}_XAXIS{sidestr}"
                    if button == "joystick1up" or button == "up":
                        return f"JOY{joynum + 1}_YAXIS{sidestr}"
                    if button == "joystick2left":
                        return f"JOY{joynum + 1}_RXAXIS{sidestr}"
                    if button == "joystick2up":
                        return f"JOY{joynum + 1}_RYAXIS{sidestr}"
                    if button == "l2":
                        return f"JOY{joynum + 1}_ZAXIS{sidestr}"
                    if button == "r2":
                        return f"JOY{joynum + 1}_RZAXIS{sidestr}"

    return None
