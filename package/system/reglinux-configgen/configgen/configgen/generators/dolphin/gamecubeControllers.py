from codecs import open as codecs_open
from pathlib import Path
from typing import Any

from configgen.utils.logger import get_logger

from .dolphinConfig import DOLPHIN_CONFIG_DIR

eslog = get_logger(__name__)


def generateControllerConfig_gamecube(
    system: Any,
    playersControllers: Any,
    wheels: Any,
    rom: str,
) -> None:
    """Generate controller configuration for GameCube controllers.

    Args:
        system: System configuration object
        playersControllers: Player controllers configuration
        wheels: Wheel controllers
        rom: ROM file path

    """
    gamecube_mapping: dict[str, str | None] = {
        "b": "Buttons/B",
        "a": "Buttons/A",
        "y": "Buttons/Y",
        "x": "Buttons/X",
        "rightshoulder": "Buttons/Z",
        "leftshoulder": None,
        "start": "Buttons/Start",
        "lefttrigger": "Triggers/L",
        "righttrigger": "Triggers/R",
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

    gamecube_reverse_axes: dict[str, str] = {
        "Main Stick/Up": "Main Stick/Down",
        "Main Stick/Left": "Main Stick/Right",
        "C-Stick/Up": "C-Stick/Down",
        "C-Stick/Left": "C-Stick/Right",
    }

    # This section allows a per ROM override of the default key options.
    configname = rom + ".cfg"  # Define ROM configuration name
    if Path(configname).is_file():  # File exists
        import ast

        with codecs_open(configname) as cconfig:
            line = cconfig.readline()
            while line:
                entry = "{" + line + "}"
                res = ast.literal_eval(entry)
                gamecube_mapping.update(res)
                line = cconfig.readline()

    generateControllerConfig_any(
        system,
        playersControllers,
        "GCPadNew.ini",
        "GCPad",
        gamecube_mapping,
        gamecube_reverse_axes,
    )


def removeControllerConfig_gamecube():
    """Remove the GameCube controller configuration file."""
    config_file_path = Path(DOLPHIN_CONFIG_DIR) / "GCPadNew.ini"
    if config_file_path.is_file():
        config_file_path.unlink()


def generateControllerConfig_any(
    system: Any,
    playersControllers: Any,
    filename: str,
    anyDefKey: str,
    anyMapping: Any,
    anyReverseAxes: Any,
) -> None:
    """Generate controller configuration for any controller type.

    Args:
        system: System configuration object
        playersControllers: Player controllers configuration
        filename: Name of the configuration file
        anyDefKey: Key for the configuration section
        anyMapping: Button mapping configuration
        anyReverseAxes: Reverse axes configuration

    """
    import codecs

    from configgen.utils.logger import get_logger

    eslog = get_logger(__name__)

    config_file_path = Path(DOLPHIN_CONFIG_DIR) / filename
    with codecs.open(str(config_file_path), "w", encoding="utf_8") as f:
        eslog.debug(f"Writing controller config to {config_file_path}")

        # In case of two pads having the same name, dolphin wants a number to handle this
        double_pads: dict[str, int] = {}

        for nplayer, pad in enumerate(sorted(playersControllers.items()), start=1):
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
                    system,
                    nplayer,
                    nsamepad,
                )


def generateControllerConfig_any_auto(
    f: Any,
    pad: Any,
    anyMapping: Any,
    anyReverseAxes: Any,
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
        system: System configuration object
        nplayer: Player number
        nsamepad: Pad number in case of multiple pads with the same name

    """
    # Use the original mapping without replacements
    current_mapping = anyMapping

    for x in pad.inputs:
        input_obj = pad.inputs[x]
        eslog.debug(f"\n ==> Processing input: {input_obj}")
        keyname = None
        if input_obj.name in current_mapping:
            keyname = current_mapping[input_obj.name]

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
        if reverse or "Trigger" in keyname:
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

        for nplayer, pad in enumerate(sorted(playersControllers.items()), start=1):
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
