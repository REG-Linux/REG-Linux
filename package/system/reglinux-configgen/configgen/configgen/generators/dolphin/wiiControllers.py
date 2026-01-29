from codecs import open as codecs_open
from pathlib import Path
from typing import Any

from configgen.utils.logger import get_logger

from .dolphinConfig import DOLPHIN_CONFIG_DIR

eslog = get_logger(__name__)


def generateControllerConfig_wii(
    system: Any,
    playersControllers: Any,
    metadata: Any,
    wheels: Any,
    rom: str,
    guns: Any,
) -> None:
    """Create the Wii controller configuration file based on the system and game settings.

    Args:
        system: System configuration object
        playersControllers: Player controllers configuration
        metadata: Game metadata
        wheels: Wheel controllers
        rom: ROM file path
        guns: Light gun controllers

    """
    if (
        system.isOptSet("use_guns")
        and system.getOptBoolean("use_guns")
        and len(guns) > 0
    ):
        generateControllerConfig_guns(
            "WiimoteNew.ini",
            "Wiimote",
            metadata,
            guns,
            system,
            rom,
        )
        from .gamecubeControllers import generateControllerConfig_gamecube

        generateControllerConfig_gamecube(
            system,
            playersControllers,
            wheels,
            rom,
        )  # You can use the gamecube pads on the wii together with wiimotes
    elif system.isOptSet("emulatedwiimotes") and not system.getOptBoolean(
        "emulatedwiimotes",
    ):
        # Generate if hardcoded
        generateControllerConfig_realwiimotes("WiimoteNew.ini", "Wiimote")
        from .gamecubeControllers import generateControllerConfig_gamecube

        generateControllerConfig_gamecube(
            system,
            playersControllers,
            wheels,
            rom,
        )  # You can use the gamecube pads on the wii together with wiimotes
    elif system.isOptSet("emulatedwiimotes") and system.getOptBoolean(
        "emulatedwiimotes",
    ):
        # Generate if hardcoded
        generateControllerConfig_emulatedwiimotes(
            system,
            playersControllers,
            wheels,
            rom,
        )
        from .gamecubeControllers import removeControllerConfig_gamecube

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
            system,
            playersControllers,
            wheels,
            rom,
        )
        from .gamecubeControllers import removeControllerConfig_gamecube

        removeControllerConfig_gamecube()  # Because pads will already be used as emulated wiimotes
    else:
        generateControllerConfig_realwiimotes("WiimoteNew.ini", "Wiimote")
        from .gamecubeControllers import generateControllerConfig_gamecube

        generateControllerConfig_gamecube(
            system,
            playersControllers,
            wheels,
            rom,
        )  # You can use the gamecube pads on the wii together with wiimotes


def generateControllerConfig_emulatedwiimotes(
    system: Any,
    playersControllers: Any,
    wheels: Any,
    rom: str,
) -> None:
    """Generate controller configuration for emulated Wiimotes.

    Args:
        system: System configuration object
        playersControllers: Player controllers configuration
        wheels: Wheel controllers
        rom: ROM file path

    """
    wii_mapping: dict[str, str] = {
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

    wii_reverse_axes: dict[str, str] = {
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

    extra_options: dict[str, str] = {"Source": "1"}

    # Side wiimote
    # triggerleft for shaking actions
    if (".side." in rom) or (
        system.isOptSet("controller_mode")
        and system.config["controller_mode"] != "disabled"
        and system.config["controller_mode"] != "cc"
    ):
        extra_options["Options/Sideways Wiimote"] = "1"
        wii_mapping["x"] = "Buttons/B"
        wii_mapping["y"] = "Buttons/A"
        wii_mapping["a"] = "Buttons/2"
        wii_mapping["b"] = "Buttons/1"
        # Note: The original code overwrites triggerleft multiple times, which is likely a bug
        # I'm preserving the original behavior but this should be reviewed
        wii_mapping["triggerleft"] = "Shake/X"
        wii_mapping["triggerleft"] = "Shake/Y"
        wii_mapping["triggerleft"] = "Shake/Z"

    # i: infrared, s: swing, t: tilt, n: nunchuk
    # 12 possible combinations : is si / it ti / in ni / st ts / sn ns / tn nt

    # i
    if (".is." in rom or ".it." in rom or ".in." in rom) or (
        system.isOptSet("controller_mode")
        and system.config["controller_mode"] != "disabled"
        and system.config["controller_mode"] != "in"
        and system.config["controller_mode"] != "cc"
    ):
        wii_mapping["lefty"] = "IR/Up"
        wii_mapping["leftx"] = "IR/Left"
    if (".si." in rom or ".ti." in rom or ".ni." in rom) or (
        system.isOptSet("controller_mode")
        and system.config["controller_mode"] == "in"
        and system.config["controller_mode"] != "cc"
    ):
        wii_mapping["righty"] = "IR/Up"
        wii_mapping["rightx"] = "IR/Left"

    # s
    if ".si." in rom or ".st." in rom or ".sn." in rom:
        wii_mapping["lefty"] = "Swing/Up"
        wii_mapping["leftx"] = "Swing/Left"
    if (".is." in rom or ".ts." in rom or ".ns." in rom) or (
        system.isOptSet("controller_mode") and system.config["controller_mode"] == "is"
    ):
        wii_mapping["righty"] = "Swing/Up"
        wii_mapping["rightx"] = "Swing/Left"

    # t
    if ".ti." in rom or ".ts." in rom or ".tn." in rom:
        wii_mapping["lefty"] = "Tilt/Forward"
        wii_mapping["leftx"] = "Tilt/Left"
    if (".it." in rom or ".st." in rom or ".nt." in rom) or (
        system.isOptSet("controller_mode") and system.config["controller_mode"] == "it"
    ):
        wii_mapping["righty"] = "Tilt/Forward"
        wii_mapping["rightx"] = "Tilt/Left"

    # n
    if (
        (".ni." in rom or ".ns." in rom or ".nt." in rom)
        or (
            system.isOptSet("controller_mode")
            and system.config["controller_mode"] == "in"
        )
        or (system.isOptSet("dsmotion") and system.getOptBoolean("dsmotion"))
    ):
        extra_options["Extension"] = "Nunchuk"
        wii_mapping["triggerleft"] = "Nunchuk/Buttons/C"
        wii_mapping["triggerright"] = "Nunchuk/Buttons/Z"
        wii_mapping["lefty"] = "Nunchuk/Stick/Up"
        wii_mapping["leftx"] = "Nunchuk/Stick/Left"
    if ".in." in rom or ".sn." in rom or ".tn." in rom:
        extra_options["Extension"] = "Nunchuk"
        wii_mapping["triggerleft"] = "Nunchuk/Buttons/C"
        wii_mapping["triggerright"] = "Nunchuk/Buttons/Z"
        wii_mapping["righty"] = "Nunchuk/Stick/Up"
        wii_mapping["rightx"] = "Nunchuk/Stick/Left"

    # cc : Classic Controller Settings / pro : Classic Controller Pro Settings
    # Swap shoulder with triggers and vice versa if cc
    if (".cc." in rom or ".pro." in rom) or (
        system.isOptSet("controller_mode")
        and system.config["controller_mode"] in ("cc", "pro")
    ):
        extra_options["Extension"] = "Classic"
        wii_mapping["x"] = "Classic/Buttons/X"
        wii_mapping["y"] = "Classic/Buttons/Y"
        wii_mapping["b"] = "Classic/Buttons/B"
        wii_mapping["a"] = "Classic/Buttons/A"
        wii_mapping["back"] = "Classic/Buttons/-"
        wii_mapping["start"] = "Classic/Buttons/+"
        wii_mapping["dpup"] = "Classic/D-Pad/Up"
        wii_mapping["dpdown"] = "Classic/D-Pad/Down"
        wii_mapping["dpleft"] = "Classic/D-Pad/Left"
        wii_mapping["dpright"] = "Classic/D-Pad/Right"
        wii_mapping["lefty"] = "Classic/Left Stick/Up"
        wii_mapping["leftx"] = "Classic/Left Stick/Left"
        wii_mapping["righty"] = "Classic/Right Stick/Up"
        wii_mapping["rightx"] = "Classic/Right Stick/Left"
        if ".cc." in rom or system.config["controller_mode"] == "cc":
            wii_mapping["leftshoulder"] = "Classic/Buttons/ZL"
            wii_mapping["rightshoulder"] = "Classic/Buttons/ZR"
            wii_mapping["triggerleft"] = "Classic/Triggers/L"
            wii_mapping["triggerright"] = "Classic/Triggers/R"
        else:
            wii_mapping["leftshoulder"] = "Classic/Triggers/L"
            wii_mapping["rightshoulder"] = "Classic/Triggers/R"
            wii_mapping["triggerleft"] = "Classic/Buttons/ZL"
            wii_mapping["triggerright"] = "Classic/Buttons/ZR"

    # This section allows a per ROM override of the default key options.
    configname = rom + ".cfg"  # Define ROM configuration name
    if Path(configname).is_file():  # File exists
        import ast

        with codecs_open(configname) as cconfig:
            line = cconfig.readline()
            while line:
                entry = "{" + line + "}"
                res = ast.literal_eval(entry)
                wii_mapping.update(res)
                line = cconfig.readline()

    eslog.debug(f"Extra Options: {extra_options}")
    eslog.debug(f"Wii Mappings: {wii_mapping}")

    generateControllerConfig_any(
        system,
        playersControllers,
        "WiimoteNew.ini",
        "Wiimote",
        wii_mapping,
        wii_reverse_axes,
        None,
        extra_options,
    )


def generateControllerConfig_realwiimotes(filename: str, anyDefKey: str) -> None:
    """Generate controller configuration for real Wiimotes.

    Args:
        filename: Name of the configuration file
        anyDefKey: Key for the configuration section

    """
    config_file_path = Path(DOLPHIN_CONFIG_DIR) / filename
    with codecs_open(str(config_file_path), "w", encoding="utf_8_sig") as f:
        nplayer = 1
        while nplayer <= 4:
            f.write(f"[{anyDefKey}{nplayer}]\n")
            f.write("Source = 2\n")
            nplayer += 1
        f.write("[BalanceBoard]\nSource = 2\n")


def generateControllerConfig_guns(
    filename: str,
    anyDefKey: str,
    metadata: Any,
    guns: Any,
    system: Any,
    rom: str,
) -> None:
    """Generate controller configuration for light guns.

    Args:
        filename: Name of the configuration file
        anyDefKey: Key for the configuration section
        metadata: Game metadata
        guns: Light gun controllers
        system: System configuration object
        rom: ROM file path

    """
    config_file_path = Path(DOLPHIN_CONFIG_DIR) / filename
    with codecs_open(str(config_file_path), "w", encoding="utf_8_sig") as f:
        # In case of two pads having the same name, dolphin wants a number to handle this
        double_pads: dict[str, int] = {}

    nplayer = 1
    while nplayer <= 4:
        if len(guns) >= nplayer:
            f.write(f"[{anyDefKey}{nplayer}]\n")
            f.write("Source = 1\n")
            f.write("Extension = Nunchuk\n")

            dolphin_mapping_names: dict[str, str] = {
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

            gun_mapping: dict[str, str] = {
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

            gun_buttons: dict[str, dict[str, str]] = {
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

            f.write(f"[{anyDefKey}{nplayer}]\n")
            f.write(f"Device = SDL/{nsamepad}/{gundevname.strip()}\n")

            buttons = guns[nplayer - 1]["buttons"]
            eslog.debug(f"Gun : {buttons}")

            # custom remapping
            # erase values
            for btn in gun_buttons:
                if "gun_" + btn in metadata:
                    for mval in metadata["gun_" + btn].split(","):
                        if mval in gun_mapping:
                            for x in gun_mapping:
                                if gun_mapping[x] == btn:
                                    eslog.info(f"erasing {x}")
                                    gun_mapping[x] = ""
                        else:
                            eslog.info(
                                f"custom gun mapping ignored for {btn} => {mval} (invalid value)",
                            )
            # setting values
            for btn in gun_buttons:
                if "gun_" + btn in metadata:
                    for mval in metadata["gun_" + btn].split(","):
                        if mval in gun_mapping:
                            gun_mapping[mval] = btn
                            eslog.info(f"setting {mval} to {btn}")

            # write buttons
            for btn in dolphin_mapping_names:
                val = ""
                if btn in gun_mapping and gun_mapping[btn] != "":
                    if gun_mapping[btn] in gun_buttons:
                        if gun_buttons[gun_mapping[btn]]["button"] in buttons:
                            val = gun_buttons[gun_mapping[btn]]["code"]
                        else:
                            eslog.debug(
                                f"gun has not the button {gun_buttons[gun_mapping[btn]]['button']}",
                            )
                    else:
                        eslog.debug(f"cannot map the button {gun_mapping[btn]}")
                f.write(f"{dolphin_mapping_names[btn]} = `{val}`\n")

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
                    f.write(f"{specifics[spe]} = {metadata['gun_' + spe]}\n")
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
    """Generate controller configuration for any controller type.

    Args:
        system: System configuration object
        playersControllers: Player controllers configuration
        filename: Name of the configuration file
        anyDefKey: Key for the configuration section
        anyMapping: Button mapping configuration
        anyReverseAxes: Reverse axes configuration
        anyReplacements: Button replacements configuration
        extraOptions: Additional options for the controller

    """
    import codecs

    from configgen.utils.logger import get_logger

    if extraOptions is None:
        extra_options: dict[str, Any] = {}
    else:
        extra_options = extraOptions

    eslog = get_logger(__name__)

    config_file_path = Path(DOLPHIN_CONFIG_DIR) / filename
    with codecs.open(str(config_file_path), "w", encoding="utf_8") as f:
        eslog.debug(f"Writing controller config to {config_file_path}")

        # In case of two pads having the same name, dolphin wants a number to handle this
        double_pads: dict[str, int] = {}

        for nplayer, (_key, pad) in enumerate(
            sorted(playersControllers.items()), start=1
        ):
            # Handle x pads having the same name
            nsamepad = double_pads.get(pad.name.strip(), 0)
            double_pads[pad.name.strip()] = nsamepad + 1

            f.write(f"[{anyDefKey}{nplayer}]\n")
            f.write(f"Device = SDL/{nsamepad}/{pad.name.strip()}\n")

            if system.isOptSet("use_pad_profiles") and system.getOptBoolean(
                "use_pad_profiles",
            ):
                if not generateControllerConfig_any_from_profiles(f, pad, system):
                    generateControllerConfig_any_auto(
                        f,
                        pad,
                        anyMapping,
                        anyReverseAxes,
                        anyReplacements,
                        extra_options,
                        system,
                        nplayer,
                        nsamepad,
                    )
            elif pad.dev in []:
                generateControllerConfig_wheel(f, pad, nplayer)
            else:
                generateControllerConfig_any_auto(
                    f,
                    pad,
                    anyMapping,
                    anyReverseAxes,
                    anyReplacements,
                    extra_options,
                    system,
                    nplayer,
                    nsamepad,
                )


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
    """Generate controller configuration automatically based on available inputs.

    Args:
        f: File object to write the configuration to
        pad: Controller pad object
        anyMapping: Button mapping configuration
        anyReverseAxes: Reverse axes configuration
        anyReplacements: Button replacements configuration
        extraOptions: Additional options for the controller
        system: System configuration object
        nplayer: Player number
        nsamepad: Pad number in case of multiple pads with the same name

    """
    for opt in extraOptions:
        if opt in ["AutoLoadState", "AutoSaveState"]:
            f.write(f"{opt} = {extraOptions[opt]}\n")

    # Recompute the mapping according to available buttons on the pads and the available replacements
    current_mapping = anyMapping
    # Apply replacements
    if anyReplacements is not None:
        for x in anyReplacements:
            if x not in pad.inputs and x in current_mapping:
                current_mapping[anyReplacements[x]] = current_mapping[x]
                if x == "lefty":
                    current_mapping[anyReplacements["joystick1down"]] = anyReverseAxes[
                        current_mapping["lefty"]
                    ]
                if x == "leftx":
                    current_mapping[anyReplacements["joystick1right"]] = anyReverseAxes[
                        current_mapping["leftx"]
                    ]
                if x == "righty":
                    current_mapping[anyReplacements["joystick2down"]] = anyReverseAxes[
                        current_mapping["righty"]
                    ]
                if x == "rightx":
                    current_mapping[anyReplacements["joystick2right"]] = anyReverseAxes[
                        current_mapping["rightx"]
                    ]

    for x in pad.inputs:
        input_obj = pad.inputs[x]

        keyname = None
        if input_obj.name in current_mapping:
            keyname = current_mapping[input_obj.name]
        elif (
            anyReplacements is not None
            and input_obj.name in anyReplacements
            and anyReplacements[input_obj.name] in current_mapping
        ):
            keyname = current_mapping[anyReplacements[input_obj.name]]

        # Write the configuration for this key
        if keyname is not None:
            write_key(
                f,
                keyname,
                input_obj.type,
                input_obj.id,
                input_obj.value,
                pad.nbaxes,
                False,
                None,
            )
            if "Triggers" in keyname and input_obj.type == "axis":
                write_key(
                    f,
                    keyname + "-Analog",
                    input_obj.type,
                    input_obj.id,
                    input_obj.value,
                    pad.nbaxes,
                    False,
                    None,
                )
        # Write the 2nd part
        if (
            input_obj.name in {"lefty", "leftx", "righty", "rightx"}
            and keyname is not None
        ):
            write_key(
                f,
                anyReverseAxes[keyname],
                input_obj.type,
                input_obj.id,
                input_obj.value,
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
        str(Path(DOLPHIN_CONFIG_DIR) / "Config" / "Profiles" / "GCPad" / "*.ini"),
    ):
        try:
            eslog.debug(f"Looking profile : {profileFile}")
            profileConfig = configparser.ConfigParser(interpolation=None)
            # To prevent ConfigParser from converting to lower case
            profileConfig.optionxform = lambda optionstr: str(optionstr)
            profileConfig.read(profileFile)
            profileDevice = profileConfig.get("Profile", "Device")
            eslog.debug(f"Profile device : {profileDevice}")

            deviceVals = re.match(r"^([^/]*)/[0-9]*/(.*)$", profileDevice)
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
    with codecs_open(configFileName, "w", encoding="utf_8_sig") as f:
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

        for nplayer, (_key, pad) in enumerate(
            sorted(playersControllers.items()), start=1
        ):
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
                    input_obj = pad.inputs[x]

                    keyname = None
                    if input_obj.name in hotkeysMapping:
                        keyname = hotkeysMapping[input_obj.name]

                    # Write the configuration for this key
                    if keyname is not None:
                        write_key(
                            f,
                            keyname,
                            input_obj.type,
                            input_obj.id,
                            input_obj.value,
                            pad.nbaxes,
                            False,
                            hotkey.id,
                        )

                        # else:
                        #    f.write("# undefined key: name="+input.name+", type="+input.type+", id="+str(input.id)+", value="+str(input.value)+"\n")
