from codecs import open
from pathlib import Path
from typing import Any

from configgen.utils.logger import get_logger

from .dolphinConfig import DOLPHIN_CONFIG_DIR

eslog = get_logger(__name__)


# Create the controller configuration file
def generateControllerConfig(
    system: Any,
    playersControllers: Any,
    metadata: Any,
    wheels: Any,
    rom: str,
    guns: Any,
) -> None:
    # generateHotkeys(playersControllers)
    if system.name == "wii":
        if (
            system.isOptSet("use_guns")
            and system.getOptBoolean("use_guns")
            and len(guns) > 0
        ):
            generateControllerConfig_guns(
                "WiimoteNew.ini", "Wiimote", metadata, guns, system, rom
            )
            generateControllerConfig_gamecube(
                system, playersControllers, wheels, rom
            )  # You can use the gamecube pads on the wii together with wiimotes
        elif system.isOptSet("emulatedwiimotes") and not system.getOptBoolean(
            "emulatedwiimotes"
        ):
            # Generate if hardcoded
            generateControllerConfig_realwiimotes("WiimoteNew.ini", "Wiimote")
            generateControllerConfig_gamecube(
                system, playersControllers, wheels, rom
            )  # You can use the gamecube pads on the wii together with wiimotes
        elif system.isOptSet("emulatedwiimotes") and system.getOptBoolean(
            "emulatedwiimotes"
        ):
            # Generate if hardcoded
            generateControllerConfig_emulatedwiimotes(
                system, playersControllers, wheels, rom
            )
            removeControllerConfig_gamecube()  # Because pads will already be used as emulated wiimotes
        elif (
            ".cc." in rom
            or ".pro." in rom
            or ".side." in rom
            or ".is." in rom
            or ".it." in rom
            or ".in." in rom
            or ".ti." in rom
            or ".ts." in rom
            or ".tn." in rom
            or ".ni." in rom
            or ".ns." in rom
            or ".nt." in rom
        ) or system.isOptSet("sideWiimote"):
            # Generate if auto and name extensions are present
            generateControllerConfig_emulatedwiimotes(
                system, playersControllers, wheels, rom
            )
            removeControllerConfig_gamecube()  # Because pads will already be used as emulated wiimotes
        else:
            generateControllerConfig_realwiimotes("WiimoteNew.ini", "Wiimote")
            generateControllerConfig_gamecube(
                system, playersControllers, wheels, rom
            )  # You can use the gamecube pads on the wii together with wiimotes
    elif system.name == "gamecube":
        used_wheels = {}
        if (
            system.isOptSet("use_wheels")
            and system.getOptBoolean("use_wheels")
            and len(wheels) > 0
        ):
            if "wheel_type" in metadata:
                if metadata["wheel_type"] == "Steering Wheel":
                    used_wheels = wheels
            elif (
                "dolphin_wheel_type" in system.config
                and system.config["dolphin_wheel_type"] == "Steering Wheel"
            ):
                used_wheels = wheels
        generateControllerConfig_gamecube(
            system, playersControllers, used_wheels, rom
        )  # Pass ROM name to allow for per ROM configuration
    else:
        raise ValueError("Invalid system name : '" + system.name + "'")


def generateControllerConfig_emulatedwiimotes(
    system: Any, playersControllers: Any, wheels: Any, rom: str
) -> None:
    wiiMapping = {
        "x": "Buttons/2",
        "b": "Buttons/A",
        "y": "Buttons/1",
        "a": "Buttons/B",
        "leftshoulder": "Buttons/-",
        "rightshoulder": "Buttons/+",
        "back": "Buttons/Home",
        "dpup": "D-Pad/Up",
        "dpdown": "D-Pad/Down",
        "dpleft": "D-Pad/Left",
        "dpright": "D-Pad/Right",
        "lefty": "IR/Up",
        "leftx": "IR/Left",
        "righty": "Tilt/Forward",
        "rightx": "Tilt/Left",
        "guide": "Buttons/Hotkey",
    }
    wiiReverseAxes = {
        "IR/Up": "IR/Down",
        "IR/Left": "IR/Right",
        "Swing/Up": "Swing/Down",
        "Swing/Left": "Swing/Right",
        "Tilt/Left": "Tilt/Right",
        "Tilt/Forward": "Tilt/Backward",
        "Nunchuk/Stick/Up": "Nunchuk/Stick/Down",
        "Nunchuk/Stick/Left": "Nunchuk/Stick/Right",
        "Classic/Right Stick/Up": "Classic/Right Stick/Down",
        "Classic/Right Stick/Left": "Classic/Right Stick/Right",
        "Classic/Left Stick/Up": "Classic/Left Stick/Down",
        "Classic/Left Stick/Left": "Classic/Left Stick/Right",
    }

    extraOptions = {}
    extraOptions["Source"] = "1"

    # Side wiimote
    # triggerleft for shaking actions
    if (".side." in rom) or (
        system.isOptSet("controller_mode")
        and system.config["controller_mode"] != "disabled"
        and system.config["controller_mode"] != "cc"
    ):
        extraOptions["Options/Sideways Wiimote"] = "1"
        wiiMapping["x"] = "Buttons/B"
        wiiMapping["y"] = "Buttons/A"
        wiiMapping["a"] = "Buttons/2"
        wiiMapping["b"] = "Buttons/1"
        wiiMapping["triggerleft"] = "Shake/X"
        wiiMapping["triggerleft"] = "Shake/Y"
        wiiMapping["triggerleft"] = "Shake/Z"

    # i: infrared, s: swing, t: tilt, n: nunchuk
    # 12 possible combinations : is si / it ti / in ni / st ts / sn ns / tn nt

    # i
    if (".is." in rom or ".it." in rom or ".in." in rom) or (
        system.isOptSet("controller_mode")
        and system.config["controller_mode"] != "disabled"
        and system.config["controller_mode"] != "in"
        and system.config["controller_mode"] != "cc"
    ):
        wiiMapping["lefty"] = "IR/Up"
        wiiMapping["leftx"] = "IR/Left"
    if (".si." in rom or ".ti." in rom or ".ni." in rom) or (
        system.isOptSet("controller_mode")
        and system.config["controller_mode"] == "in"
        and system.config["controller_mode"] != "cc"
    ):
        wiiMapping["righty"] = "IR/Up"
        wiiMapping["rightx"] = "IR/Left"

    # s
    if ".si." in rom or ".st." in rom or ".sn." in rom:
        wiiMapping["lefty"] = "Swing/Up"
        wiiMapping["leftx"] = "Swing/Left"
    if (".is." in rom or ".ts." in rom or ".ns." in rom) or (
        system.isOptSet("controller_mode") and system.config["controller_mode"] == "is"
    ):
        wiiMapping["righty"] = "Swing/Up"
        wiiMapping["rightx"] = "Swing/Left"

    # t
    if ".ti." in rom or ".ts." in rom or ".tn." in rom:
        wiiMapping["lefty"] = "Tilt/Forward"
        wiiMapping["leftx"] = "Tilt/Left"
    if (".it." in rom or ".st." in rom or ".nt." in rom) or (
        system.isOptSet("controller_mode") and system.config["controller_mode"] == "it"
    ):
        wiiMapping["righty"] = "Tilt/Forward"
        wiiMapping["rightx"] = "Tilt/Left"

    # n
    if (
        (".ni." in rom or ".ns." in rom or ".nt." in rom)
        or (
            system.isOptSet("controller_mode")
            and system.config["controller_mode"] == "in"
        )
        or (system.isOptSet("dsmotion") and system.getOptBoolean("dsmotion"))
    ):
        extraOptions["Extension"] = "Nunchuk"
        wiiMapping["triggerleft"] = "Nunchuk/Buttons/C"
        wiiMapping["triggerright"] = "Nunchuk/Buttons/Z"
        wiiMapping["lefty"] = "Nunchuk/Stick/Up"
        wiiMapping["leftx"] = "Nunchuk/Stick/Left"
    if ".in." in rom or ".sn." in rom or ".tn." in rom:
        extraOptions["Extension"] = "Nunchuk"
        wiiMapping["triggerleft"] = "Nunchuk/Buttons/C"
        wiiMapping["triggerright"] = "Nunchuk/Buttons/Z"
        wiiMapping["righty"] = "Nunchuk/Stick/Up"
        wiiMapping["rightx"] = "Nunchuk/Stick/Left"

    # cc : Classic Controller Settings / pro : Classic Controller Pro Settings
    # Swap shoulder with triggers and vice versa if cc
    if (".cc." in rom or ".pro." in rom) or (
        system.isOptSet("controller_mode")
        and system.config["controller_mode"] in ("cc", "pro")
    ):
        extraOptions["Extension"] = "Classic"
        wiiMapping["x"] = "Classic/Buttons/X"
        wiiMapping["y"] = "Classic/Buttons/Y"
        wiiMapping["b"] = "Classic/Buttons/B"
        wiiMapping["a"] = "Classic/Buttons/A"
        wiiMapping["back"] = "Classic/Buttons/-"
        wiiMapping["start"] = "Classic/Buttons/+"
        wiiMapping["dpup"] = "Classic/D-Pad/Up"
        wiiMapping["dpdown"] = "Classic/D-Pad/Down"
        wiiMapping["dpleft"] = "Classic/D-Pad/Left"
        wiiMapping["dpright"] = "Classic/D-Pad/Right"
        wiiMapping["lefty"] = "Classic/Left Stick/Up"
        wiiMapping["leftx"] = "Classic/Left Stick/Left"
        wiiMapping["righty"] = "Classic/Right Stick/Up"
        wiiMapping["rightx"] = "Classic/Right Stick/Left"
        if ".cc." in rom or system.config["controller_mode"] == "cc":
            wiiMapping["leftshoulder"] = "Classic/Buttons/ZL"
            wiiMapping["rightshoulder"] = "Classic/Buttons/ZR"
            wiiMapping["triggerleft"] = "Classic/Triggers/L"
            wiiMapping["triggerright"] = "Classic/Triggers/R"
        else:
            wiiMapping["leftshoulder"] = "Classic/Triggers/L"
            wiiMapping["rightshoulder"] = "Classic/Triggers/R"
            wiiMapping["triggerleft"] = "Classic/Buttons/ZL"
            wiiMapping["triggerright"] = "Classic/Buttons/ZR"

    # This section allows a per ROM override of the default key options.
    configname = rom + ".cfg"  # Define ROM configuration name
    if Path(configname).is_file():  # File exists
        import ast

        with open(configname) as cconfig:
            line = cconfig.readline()
            while line:
                entry = "{" + line + "}"
                res = ast.literal_eval(entry)
                wiiMapping.update(res)
                line = cconfig.readline()

    eslog.debug(f"Extra Options: {extraOptions}")
    eslog.debug(f"Wii Mappings: {wiiMapping}")

    generateControllerConfig_any(
        system,
        playersControllers,
        "WiimoteNew.ini",
        "Wiimote",
        wiiMapping,
        wiiReverseAxes,
        None,
        extraOptions,
    )


def generateControllerConfig_gamecube(
    system: Any, playersControllers: Any, wheels: Any, rom: str
) -> None:
    gamecubeMapping: dict = {
        "b": "Buttons/B",
        "a": "Buttons/A",
        "y": "Buttons/Y",
        "x": "Buttons/X",
        "rightshoulder": "Buttons/Z",
        "leftshoulder": None,
        "start": "Buttons/Start",
        "triggerleft": "Triggers/L",
        "triggerright": "Triggers/R",
        "dpup": "D-Pad/Up",
        "dpdown": "D-Pad/Down",
        "dpleft": "D-Pad/Left",
        "dpright": "D-Pad/Right",
        "lefty": "Main Stick/Up",
        "leftx": "Main Stick/Left",
        "righty": "C-Stick/Up",
        "rightx": "C-Stick/Left",
        "guide": "Buttons/Hotkey",
    }
    gamecubeReverseAxes = {
        "Main Stick/Up": "Main Stick/Down",
        "Main Stick/Left": "Main Stick/Right",
        "C-Stick/Up": "C-Stick/Down",
        "C-Stick/Left": "C-Stick/Right",
    }
    # If lefty is missing on the pad, use up instead, and if triggerleft/triggerright is missing, use l1/r1
    gamecubeReplacements = {
        "lefty": "up",
        "leftx": "left",
        "joystick1down": "down",
        "joystick1right": "right",
        "triggerleft": "leftshoulder",
        "triggerright": "rightshoulder",
    }

    # This section allows a per ROM override of the default key options.
    configname = rom + ".cfg"  # Define ROM configuration name
    if Path(configname).is_file():  # File exists
        import ast

        with open(configname) as cconfig:
            line = cconfig.readline()
            while line:
                entry = "{" + line + "}"
                res = ast.literal_eval(entry)
                gamecubeMapping.update(res)
                line = cconfig.readline()

    generateControllerConfig_any(
        system,
        playersControllers,
        "GCPadNew.ini",
        "GCPad",
        gamecubeMapping,
        gamecubeReverseAxes,
        gamecubeReplacements,
    )


def removeControllerConfig_gamecube():
    configFileName = "{}/{}".format(DOLPHIN_CONFIG_DIR, "GCPadNew.ini")
    configPath = Path(configFileName)
    if configPath.is_file():
        configPath.unlink()


def generateControllerConfig_realwiimotes(filename: str, anyDefKey: str) -> None:
    configFileName = f"{DOLPHIN_CONFIG_DIR}/{filename}"
    with open(configFileName, "w", encoding="utf_8_sig") as f:
        nplayer = 1
        while nplayer <= 4:
            f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
            f.write("Source = 2\n")
            nplayer += 1
        f.write("[BalanceBoard]\nSource = 2\n")
        f.close()


def generateControllerConfig_guns(
    filename: str, anyDefKey: str, metadata: Any, guns: Any, system: Any, rom: str
) -> None:
    configFileName = f"{DOLPHIN_CONFIG_DIR}/{filename}"
    with open(configFileName, "w", encoding="utf_8_sig") as f:
        # In case of two pads having the same name, dolphin wants a number to handle this
        double_pads = {}

    nplayer = 1
    while nplayer <= 4:
        if len(guns) >= nplayer:
            f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
            f.write("Source = 1\n")
            f.write("Extension = Nunchuk\n")

            dolphinMappingNames = {
                "a": "Buttons/A",
                "b": "Buttons/B",
                "home": "Buttons/Home",
                "-": "Buttons/-",
                "1": "Buttons/1",
                "2": "Buttons/2",
                "+": "Buttons/+",
                "up": "D-Pad/Up",
                "down": "D-Pad/Down",
                "left": "D-Pad/Left",
                "right": "D-Pad/Right",
                "tiltforward": "Tilt/Forward",
                "tiltbackward": "Tilt/Backward",
                "tiltleft": "Tilt/Left",
                "tiltright": "Tilt/Right",
                "shake": "Shake/Z",
                "c": "Nunchuk/Buttons/C",
                "z": "Nunchuk/Buttons/Z",
            }

            gunMapping = {
                "a": "action",
                "b": "trigger",
                "home": "sub3",
                "-": "select",
                "1": "sub1",
                "2": "sub2",
                "+": "start",
                "up": "up",
                "down": "down",
                "left": "left",
                "right": "right",
                "tiltforward": "",
                "tiltbackward": "",
                "tiltleft": "",
                "tiltright": "",
                "shake": "",
                "c": "",
                "z": "",
            }

            gunButtons = {
                "trigger": {"code": "BTN_LEFT", "button": "left"},
                "action": {"code": "BTN_RIGHT", "button": "right"},
                "start": {"code": "BTN_MIDDLE", "button": "middle"},
                "select": {"code": "BTN_1", "button": "1"},
                "sub1": {"code": "BTN_2", "button": "2"},
                "sub2": {"code": "BTN_3", "button": "3"},
                "sub3": {"code": "BTN_4", "button": "4"},
                "up": {"code": "BTN_5", "button": "5"},
                "down": {"code": "BTN_6", "button": "6"},
                "left": {"code": "BTN_7", "button": "7"},
                "right": {"code": "BTN_8", "button": "8"},
            }

            gundevname = guns[nplayer - 1]["name"]

            # Handle x pads having the same name
            nsamepad = 0
            if gundevname.strip() in double_pads:
                nsamepad = double_pads[gundevname.strip()]
            else:
                nsamepad = 0
                double_pads[gundevname.strip()] = nsamepad + 1

            f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
            f.write(
                "Device = SDL/"
                + str(nsamepad).strip()
                + "/"
                + gundevname.strip()
                + "\n"
            )

            buttons = guns[nplayer - 1]["buttons"]
            eslog.debug(f"Gun : {buttons}")

            # custom remapping
            # erase values
            for btn in gunButtons:
                if "gun_" + btn in metadata:
                    for mval in metadata["gun_" + btn].split(","):
                        if mval in gunMapping:
                            for x in gunMapping:
                                if gunMapping[x] == btn:
                                    eslog.info(f"erasing {x}")
                                    gunMapping[x] = ""
                        else:
                            eslog.info(
                                f"custom gun mapping ignored for {btn} => {mval} (invalid value)"
                            )
            # setting values
            for btn in gunButtons:
                if "gun_" + btn in metadata:
                    for mval in metadata["gun_" + btn].split(","):
                        if mval in gunMapping:
                            gunMapping[mval] = btn
                            eslog.info(f"setting {mval} to {btn}")

            # write buttons
            for btn in dolphinMappingNames:
                val = ""
                if btn in gunMapping and gunMapping[btn] != "":
                    if gunMapping[btn] in gunButtons:
                        if gunButtons[gunMapping[btn]]["button"] in buttons:
                            val = gunButtons[gunMapping[btn]]["code"]
                        else:
                            eslog.debug(
                                "gun has not the button {}".format(
                                    gunButtons[gunMapping[btn]]["button"]
                                )
                            )
                    else:
                        eslog.debug(f"cannot map the button {gunMapping[btn]}")
                f.write(dolphinMappingNames[btn] + " = `" + val + "`\n")

            # map ir
            if "gun_" + "ir_up" not in metadata:
                f.write("IR/Up = `Axis 1-`\n")
            if "gun_" + "ir_down" not in metadata:
                f.write("IR/Down = `Axis 1+`\n")
            if "gun_" + "ir_left" not in metadata:
                f.write("IR/Left = `Axis 0-`\n")
            if "gun_" + "ir_right" not in metadata:
                f.write("IR/Right = `Axis 0+`\n")

            # specific games configurations
            specifics = {
                "vertical_offset": "IR/Vertical Offset",
                "yaw": "IR/Total Yaw",
                "pitch": "IR/Total Pitch",
                "ir_up": "IR/Up",
                "ir_down": "IR/Down",
                "ir_left": "IR/Left",
                "ir_right": "IR/Right",
            }
            for spe in specifics:
                if "gun_" + spe in metadata:
                    f.write("{} = {}\n".format(specifics[spe], metadata["gun_" + spe]))
        nplayer += 1
    f.close()


def generateControllerConfig_any(
    system: Any,
    playersControllers: Any,
    filename: str,
    anyDefKey: str,
    anyMapping: Any,
    anyReverseAxes: Any,
    anyReplacements: Any,
    extraOptions: dict[str, Any] | None = None,
) -> None:
    import codecs

    from configgen.utils.logger import get_logger

    if extraOptions is None:
        extraOptions = {}

    eslog = get_logger(__name__)

    configFileName = str(Path(DOLPHIN_CONFIG_DIR) / filename)
    with codecs.open(configFileName, "w", encoding="utf_8") as f:
        eslog.debug(f"Writing controller config to {configFileName}")
        nplayer = 1
        nsamepad = 0

        # In case of two pads having the same name, dolphin wants a number to handle this
        double_pads = {}

        for _, pad in sorted(playersControllers.items()):
            # Handle x pads having the same name
            nsamepad = double_pads.get(pad.name.strip(), 0)
            double_pads[pad.name.strip()] = nsamepad + 1

            f.write("[" + anyDefKey + str(nplayer) + "]" + "\n")
            f.write(
                "Device = SDL/" + str(nsamepad).strip() + "/" + pad.name.strip() + "\n"
            )

            if system.isOptSet("use_pad_profiles") and system.getOptBoolean(
                "use_pad_profiles"
            ):
                if not generateControllerConfig_any_from_profiles(f, pad, system):
                    generateControllerConfig_any_auto(
                        f,
                        pad,
                        anyMapping,
                        anyReverseAxes,
                        anyReplacements,
                        extraOptions,
                        system,
                        nplayer,
                        nsamepad,
                    )
            else:
                if pad.dev in []:
                    generateControllerConfig_wheel(f, pad, nplayer)
                else:
                    generateControllerConfig_any_auto(
                        f,
                        pad,
                        anyMapping,
                        anyReverseAxes,
                        anyReplacements,
                        extraOptions,
                        system,
                        nplayer,
                        nsamepad,
                    )

            nplayer += 1


def generateControllerConfig_any_auto(
    f: Any,
    pad: Any,
    anyMapping: Any,
    anyReverseAxes: Any,
    anyReplacements: Any,
    extraOptions: Any,
    system: Any,
    nplayer: int,
    nsamepad: int,
) -> None:
    for opt in extraOptions:
        if opt in ["AutoLoadState", "AutoSaveState"]:
            f.write(opt + " = " + extraOptions[opt] + "\n")

    # Recompute the mapping according to available buttons on the pads and the available replacements
    currentMapping = anyMapping
    # Apply replacements
    if anyReplacements is not None:
        for x in anyReplacements:
            if x not in pad.inputs and x in currentMapping:
                currentMapping[anyReplacements[x]] = currentMapping[x]
                if x == "lefty":
                    currentMapping[anyReplacements["joystick1down"]] = anyReverseAxes[
                        currentMapping["lefty"]
                    ]
                if x == "leftx":
                    currentMapping[anyReplacements["joystick1right"]] = anyReverseAxes[
                        currentMapping["leftx"]
                    ]
                if x == "righty":
                    currentMapping[anyReplacements["joystick2down"]] = anyReverseAxes[
                        currentMapping["righty"]
                    ]
                if x == "rightx":
                    currentMapping[anyReplacements["joystick2right"]] = anyReverseAxes[
                        currentMapping["rightx"]
                    ]

    for x in pad.inputs:
        input = pad.inputs[x]

        keyname = None
        if input.name in currentMapping:
            keyname = currentMapping[input.name]
        elif (
            anyReplacements is not None
            and input.name in anyReplacements
            and anyReplacements[input.name] in currentMapping
        ):
            keyname = currentMapping[anyReplacements[input.name]]

        # Write the configuration for this key
        if keyname is not None:
            write_key(
                f, keyname, input.type, input.id, input.value, pad.nbaxes, False, None
            )
            if "Triggers" in keyname and input.type == "axis":
                write_key(
                    f,
                    keyname + "-Analog",
                    input.type,
                    input.id,
                    input.value,
                    pad.nbaxes,
                    False,
                    None,
                )
        # Write the 2nd part
        if input.name in {"lefty", "leftx", "righty", "rightx"} and keyname is not None:
            write_key(
                f,
                anyReverseAxes[keyname],
                input.type,
                input.id,
                input.value,
                pad.nbaxes,
                True,
                None,
            )
        # Rumble option
        if system.isOptSet("rumble") and system.getOptBoolean("rumble"):
            f.write("Rumble/Motor = Weak\n")


def generateControllerConfig_any_from_profiles(f: Any, pad: Any, system: Any) -> bool:
    import configparser
    import glob
    import re

    from configgen.utils.logger import get_logger

    eslog = get_logger(__name__)

    for profileFile in glob.glob(
        str(Path(DOLPHIN_CONFIG_DIR) / "Config" / "Profiles" / "GCPad" / "*.ini")
    ):
        try:
            eslog.debug(f"Looking profile : {profileFile}")
            profileConfig = configparser.ConfigParser(interpolation=None)
            # To prevent ConfigParser from converting to lower case
            profileConfig.optionxform = lambda optionstr: str(optionstr)
            profileConfig.read(profileFile)
            profileDevice = profileConfig.get("Profile", "Device")
            eslog.debug(f"Profile device : {profileDevice}")

            deviceVals = re.match("^([^/]*)/[0-9]*/(.*)$", profileDevice)
            if deviceVals is not None and (
                deviceVals.group(1) == "SDL"
                and deviceVals.group(2).strip() == pad.name.strip()
            ):
                eslog.debug("Eligible profile device found")
                for key, val in profileConfig.items("Profile"):
                    if key != "Device":
                        f.write(f"{key} = {val}\n")
                return True
        except Exception:
            eslog.error(f"profile {profileFile} : FAILED")

    return False


def generateControllerConfig_wheel(f: Any, pad: Any, nplayer: int) -> None:
    # Placeholder implementation for wheel configuration
    # This function would handle wheel-specific controller configuration
    f.write(f"# Wheel configuration for player {nplayer}\n")
    f.write("Extension = Wheel\n")


def write_key(
    f: Any,
    keyname: str,
    input_type: str,
    input_id: str,
    input_value: str,
    input_global_id: str,
    reverse: bool,
    hotkey_id: str | None,
) -> None:
    f.write(keyname + " = ")
    if hotkey_id is not None:
        f.write("`Button " + str(hotkey_id) + "` & ")
    f.write("`")
    if input_type == "button":
        f.write("Button " + str(input_id))
    elif input_type == "hat":
        if input_id == "h0.1":  # up
            f.write("Pad N")
        elif input_id == "h0.4":  # down
            f.write("Pad S")
        elif input_id == "h0.8":  # left
            f.write("Pad W")
        elif input_id == "h0.2":  # right
            f.write("Pad E")
    elif input_type == "axis":
        if reverse:
            f.write("Axis " + str(input_id) + "+")
        else:
            f.write("Axis " + str(input_id) + "-")
    f.write("`\n")


def generateHotkeys(playersControllers: Any) -> None:
    configFileName = str(Path(DOLPHIN_CONFIG_DIR) / "Hotkeys.ini")
    with open(configFileName, "w", encoding="utf_8_sig") as f:
        hotkeysMapping = {
            "a": "Keys/Reset",
            "b": "Keys/Toggle Pause",
            "x": "Keys/Load from selected slot",
            "y": "Keys/Save to selected slot",
            "triggerright": None,
            "start": "Keys/Exit",
            "leftshoulder": "Keys/Take Screenshot",
            "rightshoulder": "Keys/Toggle 3D Side-by-side",
            "dpup": "Keys/Increase Selected State Slot",
            "dpdown": "Keys/Decrease Selected State Slot",
            "dpleft": None,
            "dpright": None,
            "lefty": None,
            "leftx": None,
            "righty": None,
            "rightx": None,
        }

        nplayer = 1
        for _, pad in sorted(playersControllers.items()):
            if nplayer == 1:
                f.write("[Hotkeys1]" + "\n")
                f.write("Device = SDL/0/" + pad.name.strip() + "\n")

                # Search the hotkey button
                hotkey = None
                if "guide" not in pad.inputs:
                    return
                hotkey = pad.inputs["guide"]
                if hotkey.type != "button":
                    return

                for x in pad.inputs:
                    input = pad.inputs[x]

                    keyname = None
                    if input.name in hotkeysMapping:
                        keyname = hotkeysMapping[input.name]

                    # Write the configuration for this key
                    if keyname is not None:
                        write_key(
                            f,
                            keyname,
                            input.type,
                            input.id,
                            input.value,
                            pad.nbaxes,
                            False,
                            hotkey.id,
                        )

                        # else:
                        #    f.write("# undefined key: name="+input.name+", type="+input.type+", id="+str(input.id)+", value="+str(input.value)+"\n")

            nplayer += 1
