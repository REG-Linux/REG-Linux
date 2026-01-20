"""Event Mapper (Evmapy) Module.

This module provides functionality to map gamepad/controller inputs to keyboard events
for game emulation systems. It handles the configuration and management of input
mapping between physical controllers and virtual keyboard/mouse events.

The main purpose is to allow gamepads to control games that expect keyboard input
by translating gamepad button presses and analog stick movements into corresponding
keyboard key presses or mouse movements.
"""

import os
from json import dumps, load
from pathlib import Path
from subprocess import call
from typing import Any

from evdev import InputDevice

from configgen.utils.logger import get_logger

from .mouse import mouseButtonToCode

eslog = get_logger(__name__)


class Evmapy:
    """Event Mapper class for handling gamepad to keyboard/mouse input mapping.

    This class manages the process that maps gamepad inputs to keyboard events,
    allowing controllers to be used with games that expect keyboard input.
    """

    # Track whether the evmapy process has been started
    __started = False

    @staticmethod
    def start(
        system: Any,
        emulator: str,
        core: str,
        rom: str,
        players_controllers: dict[str, Any],
        guns: dict[str, Any] | list[dict[str, Any]],
    ) -> None:
        """Start the evmapy process with the given configuration.

        Args:
            system (str): The game system name (e.g., 'snes', 'nes', 'arcade')
            emulator (str): The emulator being used
            core (str): The emulator core being used
            rom (str): Path to the ROM file or directory
            players_controllers (dict): Dictionary mapping player numbers to controller objects
            guns (dict): Dictionary of light gun configurations

        Returns:
            None

        """
        if Evmapy.__prepare(system, emulator, core, rom, players_controllers, guns):
            Evmapy.__started = True
            call(["system-evmapy", "start"])

    @staticmethod
    def stop():
        """Stop the evmapy process if it's currently running.

        Returns:
            None

        """
        if Evmapy.__started:
            Evmapy.__started = False
            call(["system-evmapy", "stop"])

    @staticmethod
    def __prepare(
        system: Any,
        emulator: str,
        core: str,
        rom: str,
        players_controllers: dict[str, Any],
        guns: dict[str, Any] | list[dict[str, Any]],
    ) -> bool:
        """Prepare evmapy configuration files for the given system and controllers.

        This method searches for configuration files in a specific order of precedence
        and generates the necessary JSON configuration files for each controller.

        Configuration file search order:
        1. ROM-specific config: {rom}.keys
        2. ROM directory config: {rom}/padto.keys
        3. System-specific config: /userdata/system/configs/evmapy/{system}.keys
        4. System+emulator config: /usr/share/evmapy/{system}.{emulator}.keys
        5. System default config: /usr/share/evmapy/{system}.keys

        Args:
            system (str): The game system name
            emulator (str): The emulator being used
            core (str): The emulator core being used
            rom (str): Path to the ROM file or directory
            players_controllers (dict): Dictionary mapping player numbers to controller objects
            guns (dict): Dictionary of light gun configurations

        Returns:
            bool: True if configuration was successfully prepared, False otherwise

        """
        # Search for configuration files in order of precedence
        for keysfile in [
            f"{rom}.keys",  # ROM-specific configuration
            f"{rom}/padto.keys",  # Configuration inside ROM directory
            # Commented out more specific configurations for now
            # str(Path("/userdata/system/configs/evmapy") / f"{system}.{emulator}.{core}.keys"),
            # str(Path("/userdata/system/configs/evmapy") / f"{system}.{emulator}.keys"),
            str(
                Path("/userdata/system/configs/evmapy") / f"{system}.keys",
            ),  # User system config
            # System-wide configurations
            # str(Path("/usr/share/evmapy") / f"{system}.{emulator}.{core}.keys"),
            str(
                Path("/usr/share/evmapy") / f"{system}.{emulator}.keys",
            ),  # System+emulator config
            str(Path("/usr/share/evmapy") / f"{system}.keys"),  # Default system config
        ]:
            # Check if configuration file exists and handle directory ROM case
            keysfile_path = Path(keysfile)
            if (keysfile_path.is_absolute() and keysfile_path.exists()) or (
                (not keysfile_path.is_absolute() and Path(keysfile).exists())
                and not (Path(rom).is_dir() and keysfile == f"{rom}.keys")
            ):
                eslog.debug(f"evmapy on {keysfile}")

                # Clear any existing evmapy configuration
                call(["system-evmapy", "clear"])

                # Load the pad action configuration from the keys file
                try:
                    with Path(keysfile).open() as f:
                        padActionConfig: dict[str, Any] = load(f)
                except OSError as e:
                    eslog.error(f"Error loading keys file {keysfile}: {e}")
                    # Continue with empty padActionConfig to avoid breaking the process
                    padActionConfig: dict[str, Any] = {}

                # Configure light guns
                # Handle both dict and list formats for backwards compatibility
                if isinstance(guns, dict):
                    # For dict format: enumerate the items to get consistent indexing
                    guns_enum = enumerate(guns.items(), start=1)
                else:
                    # For list format: enumerate the list to get index and value
                    guns_enum = enumerate(guns, start=1)

                for item in guns_enum:
                    if isinstance(guns, dict):
                        # For dict format: item is (index, (key, value))
                        ngun, (_, gun) = item
                        # Type guard to ensure gun is a dict
                        if not isinstance(gun, dict):
                            continue
                        gun_node = gun["node"]
                        gun_buttons = gun["buttons"]
                    else:
                        # For list format: item is (index, value)
                        ngun, gun = item
                        # Type guard to ensure gun is a dict
                        if not isinstance(gun, dict):
                            continue
                        gun_node = gun["node"]
                        gun_buttons = gun["buttons"]

                    gun_action_key = "actions_gun" + str(ngun)
                    if gun_action_key in padActionConfig:
                        # Generate configuration file path for this gun
                        configfile = str(
                            Path("/var/run/evmapy") / f"{Path(gun_node).name}.json",
                        )
                        eslog.debug(
                            f"config file for keysfile is {configfile} (from {keysfile}) - gun",
                        )

                        # Initialize gun configuration structure
                        padConfig: dict[str, Any] = {}
                        padConfig["buttons"] = []
                        padConfig["axes"] = []
                        padConfig["actions"] = []

                        # Add gun buttons to configuration
                        for button in gun_buttons:
                            padConfig["buttons"].append(
                                {"name": button, "code": mouseButtonToCode(button)},
                            )
                        padConfig["grab"] = False

                        # Process gun actions from the configuration
                        gun_actions: list[dict[str, Any]] = padActionConfig[
                            gun_action_key
                        ]
                        for action in gun_actions:
                            action: dict[str, Any]
                            if (
                                "trigger" in action
                                and "type" in action
                                and "target" in action
                            ):
                                guntrigger = Evmapy.__getGunTrigger(
                                    action["trigger"],
                                    gun,
                                )

                                if guntrigger:
                                    newaction: dict[str, Any] = action.copy()
                                    # Remove description field as it's not needed in runtime config
                                    newaction.pop("description", None)
                                    newaction["trigger"] = guntrigger
                                    padConfig["actions"].append(newaction)

                        # Write gun configuration to file
                        Path(configfile).write_text(dumps(padConfig, indent=4))

                # Configure each player's controller
                for nplayer, (_, pad) in enumerate(
                    sorted(players_controllers.items()),
                    start=1,
                ):
                    player_action_key = "actions_player" + str(nplayer)
                    if player_action_key in padActionConfig:
                        # Generate configuration file path for this controller
                        configfile = str(
                            Path("/var/run/evmapy") / f"{Path(pad.dev).name}.json",
                        )
                        eslog.debug(
                            f"config file for keysfile is {configfile} (from {keysfile})",
                        )

                        # Initialize controller configuration structure
                        padConfig: dict[str, Any] = {}
                        padConfig["axes"] = []
                        padConfig["buttons"] = []
                        padConfig["grab"] = False

                        # Track axis orientation for proper mapping
                        absbasex_positive = (
                            True  # Determines if right is positive for base X axis
                        )
                        absbasey_positive = (
                            True  # Determines if down is positive for base Y axis
                        )

                        # Initialize tracking dictionaries for controller inputs
                        known_buttons_names: dict[
                            str,
                            Any,
                        ] = {}  # Buttons available on this controller
                        known_buttons_codes: dict[
                            int,
                            str,
                        ] = {}  # Map button codes to names
                        known_buttons_alias: dict[
                            str,
                            str,
                        ] = {}  # Alternative names for buttons
                        known_axes_codes: dict[
                            int,
                            bool,
                        ] = {}  # Axes available on this controller

                        # Handle controllers where guide and back buttons share the same code
                        guide_equal_back = (
                            pad.inputs["guide"].value == pad.inputs["back"].value
                        )

                        # Process all inputs from the controller
                        for index in pad.inputs:
                            input_obj = pad.inputs[index].sdl_to_linux_input_event(
                                guide_equal_back,
                            )
                            if input_obj is None:
                                continue

                            if input_obj["type"] == "button":
                                # Add button to configuration (avoid duplicates)
                                if input_obj["code"] is not None:
                                    if input_obj["code"] not in known_buttons_codes:
                                        known_buttons_names[input_obj["name"]] = True
                                        known_buttons_codes[input_obj["code"]] = (
                                            input_obj["name"]
                                        )
                                        padConfig["buttons"].append(
                                            {
                                                "name": input_obj["name"],
                                                "code": int(input_obj["code"]),
                                            },
                                        )
                                    else:
                                        # Create alias for duplicate button codes
                                        known_buttons_alias[input_obj["name"]] = (
                                            known_buttons_codes[input_obj["code"]]
                                        )

                            elif input_obj["type"] == "hat":
                                # Handle D-pad (hat) inputs - only process X and Y values once
                                if int(input_obj["value"]) in [
                                    1,
                                    2,
                                ]:  # Don't duplicate values
                                    if int(input_obj["value"]) == 1:
                                        name = "X"
                                        isYAsInt = 0
                                    else:
                                        name = "Y"
                                        isYAsInt = 1

                                    # Add hat axis min/max buttons
                                    hat_name_min = (
                                        "HAT" + input_obj["id"] + name + ":min"
                                    )
                                    hat_name_max = (
                                        "HAT" + input_obj["id"] + name + ":max"
                                    )
                                    known_buttons_names[hat_name_min] = True
                                    known_buttons_names[hat_name_max] = True

                                    padConfig["axes"].append(
                                        {
                                            "name": "HAT" + input_obj["id"] + name,
                                            "code": int(input_obj["id"])
                                            + 16
                                            + isYAsInt,  # 16 = HAT0X in linux/input.h
                                            "min": -1,
                                            "max": 1,
                                        },
                                    )

                            elif (
                                input_obj["type"] == "axis"
                                and input_obj["code"] not in known_axes_codes
                            ):
                                # Handle analog stick and trigger inputs, avoid duplicates
                                known_axes_codes[input_obj["code"]] = True
                                axisId: str | None = None
                                axisName: str | None = None

                                # Map axis inputs to standardized names
                                if input_obj["name"] in [
                                    "joystick1up",
                                    "joystick1left",
                                ]:
                                    axisId = "0"  # Left analog stick
                                elif input_obj["name"] in [
                                    "joystick2up",
                                    "joystick2left",
                                ]:
                                    axisId = "1"  # Right analog stick

                                if input_obj["name"] in [
                                    "joystick1up",
                                    "joystick2up",
                                ]:
                                    axisName = "Y"
                                elif input_obj["name"] in [
                                    "joystick1left",
                                    "joystick2left",
                                ]:
                                    axisName = "X"
                                elif input_obj["name"] in ["up", "down"]:
                                    # D-pad implemented as axis
                                    axisId = "BASE"
                                    axisName = "Y"
                                    if input_obj["name"] == "up":
                                        absbasey_positive = int(input_obj["value"]) >= 0
                                    else:
                                        axisId = None  # Don't duplicate, configure only for 'up'
                                elif input_obj["name"] in ["left", "right"]:
                                    # D-pad implemented as axis
                                    axisId = "BASE"
                                    axisName = "X"
                                    if input_obj["name"] == "left":
                                        absbasex_positive = int(input_obj["value"]) < 0
                                    else:
                                        axisId = None  # Don't duplicate, configure only for 'left'
                                else:
                                    # Other axes (triggers, etc.)
                                    axisId = "_OTHERS_"
                                    axisName = input_obj["name"]

                                # Add axis configuration if valid
                                if (
                                    (
                                        axisId in ["0", "1", "BASE"]
                                        and axisName in ["X", "Y"]
                                    )
                                    or axisId == "_OTHERS_"
                                ) and input_obj["code"] is not None:
                                    axisMin, axisMax = Evmapy.__getPadMinMaxAxis(
                                        pad.dev,
                                        int(input_obj["code"]),
                                    )

                                    # Add axis virtual buttons (min, max, val)
                                    if axisId is not None and axisName is not None:
                                        axis_base_name = "ABS" + axisId + axisName
                                        known_buttons_names[axis_base_name + ":min"] = (
                                            True
                                        )
                                        known_buttons_names[axis_base_name + ":max"] = (
                                            True
                                        )
                                        known_buttons_names[axis_base_name + ":val"] = (
                                            True
                                        )

                                        padConfig["axes"].append(
                                            {
                                                "name": axis_base_name,
                                                "code": int(input_obj["code"]),
                                                "min": axisMin,
                                                "max": axisMax,
                                            },
                                        )

                        # Process actions from configuration file
                        padActionsPreDefined: list[dict[str, Any]] = padActionConfig[
                            player_action_key
                        ]
                        padActionsFiltered: list[dict[str, Any]] = []

                        # Handle mouse events - expand joystick shortcuts to x/y components
                        padActionsDefined: list[dict[str, Any]] = []
                        for action in padActionsPreDefined:
                            if (
                                "type" in action
                                and action["type"] == "mouse"
                                and "target" not in action
                                and "trigger" in action
                            ):
                                if action["trigger"] == "joystick1":
                                    # Split joystick1 into x and y components
                                    newaction: dict[str, Any] = action.copy()
                                    newaction["trigger"] = "joystick1x"
                                    newaction["target"] = "X"
                                    padActionsDefined.append(newaction)

                                    newaction = action.copy()
                                    newaction["trigger"] = "joystick1y"
                                    newaction["target"] = "Y"
                                    padActionsDefined.append(newaction)

                                elif action["trigger"] == "joystick2":
                                    # Split joystick2 into x and y components
                                    newaction: dict[str, Any] = action.copy()
                                    newaction["trigger"] = "joystick2x"
                                    newaction["target"] = "X"
                                    padActionsDefined.append(newaction)

                                    newaction = action.copy()
                                    newaction["trigger"] = "joystick2y"
                                    newaction["target"] = "Y"
                                    padActionsDefined.append(newaction)
                            else:
                                padActionsDefined.append(action)

                        # Filter actions to only include those with valid triggers
                        for action in padActionsDefined:
                            if "trigger" in action:
                                # Map the trigger to the actual controller input
                                trigger = Evmapy.__trigger_mapper(
                                    action["trigger"],
                                    known_buttons_alias,
                                    known_buttons_names,
                                    absbasex_positive,
                                    absbasey_positive,
                                )

                                # Set default mode if not specified
                                if "mode" not in action:
                                    mode = Evmapy.__trigger_mapper_mode(
                                        action["trigger"],
                                    )
                                    if mode is not None:
                                        action["mode"] = mode

                                action["trigger"] = trigger

                                # Validate that all triggers exist on this controller
                                if isinstance(trigger, list):
                                    allfound = True
                                    for x in trigger:
                                        if (
                                            x not in known_buttons_names
                                            and ("ABS_OTHERS_" + x + ":max")
                                            not in known_buttons_names
                                        ):
                                            allfound = False
                                    if allfound:
                                        # Rewrite axis buttons for special axes
                                        if isinstance(action["trigger"], list):
                                            for i, val in enumerate(trigger):
                                                if (
                                                    "ABS_OTHERS_" + val + ":max"
                                                    in known_buttons_names
                                                ):
                                                    action["trigger"][i] = (
                                                        "ABS_OTHERS_" + val + ":max"
                                                    )
                                        padActionsFiltered.append(action)
                                # Single trigger validation
                                elif trigger in known_buttons_names:
                                    padActionsFiltered.append(action)
                                elif (
                                    "ABS_OTHERS_" + trigger + ":max"
                                    in known_buttons_names
                                ):
                                    action["trigger"] = "ABS_OTHERS_" + trigger + ":max"
                                    padActionsFiltered.append(action)

                        padConfig["actions"] = padActionsFiltered

                        # Clean up configuration by removing description fields
                        for action in padConfig["actions"]:
                            if "description" in action:
                                del action["description"]

                        # Optimize axis ranges based on usage
                        # Use full axis range for mouse, 50% range for keys
                        axis_for_mouse: dict[str, bool] = {}
                        for action in padConfig["actions"]:
                            if "type" in action and action["type"] == "mouse":
                                if isinstance(action["trigger"], list):
                                    for x in action["trigger"]:
                                        if isinstance(x, str):
                                            axis_for_mouse[x] = True
                                else:
                                    trigger_value = action["trigger"]
                                    if isinstance(trigger_value, str):
                                        axis_for_mouse[trigger_value] = True

                        # Adjust axis ranges for non-mouse actions
                        for axis in padConfig["axes"]:
                            axis_name: str = (
                                axis["name"]
                                if isinstance(axis, dict) and "name" in axis
                                else ""
                            )
                            axis_triggers: list[str] = [
                                axis_name + ":val",
                                axis_name + ":min",
                                axis_name + ":max",
                            ]
                            if not any(
                                isinstance(trigger, str) and trigger in axis_for_mouse
                                for trigger in axis_triggers
                            ):
                                min_val, max_val = Evmapy.__getPadMinMaxAxisForKeys(
                                    axis["min"],
                                    axis["max"],
                                )
                                axis["min"] = min_val
                                axis["max"] = max_val

                        # Write controller configuration to file
                        Path(configfile).write_text(dumps(padConfig, indent=4))

                return True

        # No configuration file found
        eslog.debug(
            f"no evmapy config file found for system={system}, emulator={emulator}",
        )
        return False

    @staticmethod
    def __trigger_mapper(
        trigger: str,
        known_buttons_alias: dict[str, str],
        known_buttons_names: dict[str, Any],
        absbasex_positive: int,
        absbasey_positive: int,
    ) -> str | list[str]:
        """Map evmapy trigger names to actual controller input names.

        This function translates generic trigger names (like 'up', 'joystick1left')
        to specific controller input names (like 'HAT0Y:max', 'ABS0X:min').

        Args:
            trigger: Either a string or list of trigger names to map
            known_buttons_alias (dict): Button aliases for this controller
            known_buttons_names (dict): Available button names for this controller (key existence checked only)
            absbasex_positive (bool): Whether right is positive for base X axis
            absbasey_positive (bool): Whether down is positive for base Y axis

        Returns:
            Mapped trigger name(s) - string or list depending on input

        """
        if isinstance(trigger, list):
            return [
                Evmapy.__trigger_mapper_string(
                    x,
                    known_buttons_alias,
                    known_buttons_names,
                    absbasex_positive,
                    absbasey_positive,
                )
                for x in trigger
            ]
        return Evmapy.__trigger_mapper_string(
            trigger,
            known_buttons_alias,
            known_buttons_names,
            absbasex_positive,
            absbasey_positive,
        )

    @staticmethod
    def __trigger_mapper_string(
        trigger: str,
        known_buttons_alias: dict[str, str],
        known_buttons_names: dict[str, Any],
        absbasex_positive: int,
        absbasey_positive: int,
    ) -> str:
        """Map a single trigger string to the appropriate controller input name.

        Args:
            trigger (str): The trigger name to map
            known_buttons_alias (dict): Button aliases for this controller
            known_buttons_names (dict): Available button names for this controller (key existence checked only)
            absbasex_positive (bool): Whether right is positive for base X axis
            absbasey_positive (bool): Whether down is positive for base Y axis

        Returns:
            str or list: Mapped trigger name(s)

        """
        # Standard mapping for analog sticks
        mapping = {
            # Left analog stick
            "joystick1right": "ABS0X:max",
            "joystick1left": "ABS0X:min",
            "joystick1down": "ABS0Y:max",
            "joystick1up": "ABS0Y:min",
            # Right analog stick
            "joystick2right": "ABS1X:max",
            "joystick2left": "ABS1X:min",
            "joystick2down": "ABS1Y:max",
            "joystick2up": "ABS1Y:min",
            # Analog stick mouse movement (returns full axis range)
            "joystick1x": ["ABS0X:val", "ABS0X:min", "ABS0X:max"],
            "joystick1y": ["ABS0Y:val", "ABS0Y:min", "ABS0Y:max"],
            "joystick2x": ["ABS1X:val", "ABS1X:min", "ABS1X:max"],
            "joystick2y": ["ABS1Y:val", "ABS1Y:min", "ABS1Y:max"],
        }

        # Map D-pad directions based on available input types
        if "HAT0X:min" in known_buttons_names:
            # D-pad implemented as hat switch
            mapping["left"] = "HAT0X:min"
            mapping["right"] = "HAT0X:max"
            mapping["down"] = "HAT0Y:max"
            mapping["up"] = "HAT0Y:min"

        if "ABSBASEX:min" in known_buttons_names:
            # D-pad implemented as analog axis - handle orientation
            if absbasex_positive:
                mapping["left"] = "ABSBASEX:min"
                mapping["right"] = "ABSBASEX:max"
            else:
                mapping["left"] = "ABSBASEX:max"
                mapping["right"] = "ABSBASEX:min"

        if "ABSBASEY:min" in known_buttons_names:
            # D-pad Y axis - handle orientation
            if absbasey_positive:
                mapping["down"] = "ABSBASEY:max"
                mapping["up"] = "ABSBASEY:min"
            else:
                mapping["down"] = "ABSBASEY:min"
                mapping["up"] = "ABSBASEY:max"

        # Check for button aliases first
        if trigger in known_buttons_alias:
            return known_buttons_alias[trigger]

        # Apply mapping if available
        if trigger in mapping:
            if isinstance(mapping[trigger], list):
                # For list mappings, ensure all components exist
                all_found = True
                for x in mapping[trigger]:
                    if x not in known_buttons_names:
                        all_found = False
                if all_found:
                    return mapping[trigger]
            elif mapping[trigger] in known_buttons_names:
                return mapping[trigger]

        return trigger  # Return unchanged if no mapping found

    @staticmethod
    def __trigger_mapper_mode(trigger: str | list[str]) -> str | None:
        """Determine the appropriate mode for a trigger.

        Args:
            trigger: Trigger name or list of trigger names

        Returns:
            str or None: The mode to use for this trigger type

        """
        if isinstance(trigger, list):
            for x in trigger:
                mode = Evmapy.__trigger_mapper_mode_string(x)
                if mode is not None:
                    return mode
            return None
        return Evmapy.__trigger_mapper_mode_string(trigger)

    @staticmethod
    def __trigger_mapper_mode_string(trigger: str) -> str | None:
        """Determine the mode for a single trigger string.

        Analog stick mouse movement should use "any" mode to allow
        movement in any direction without requiring the stick to return
        to center position.

        Args:
            trigger (str): The trigger name

        Returns:
            str or None: "any" for analog mouse triggers, None otherwise

        """
        if trigger in ["joystick1x", "joystick1y", "joystick2x", "joystick2y"]:
            return "any"
        return None

    @staticmethod
    def __getGunTrigger(
        trigger: str | list[str],
        gun: dict[str, Any],
    ) -> str | list[str] | None:
        """Validate that gun trigger(s) are available on the specified gun device.

        Args:
            trigger: Button name or list of button names
            gun (dict): Gun configuration containing available buttons

        Returns:
            The original trigger if valid, None if any button is not available

        """
        if isinstance(trigger, list):
            # All buttons in the list must be available
            for button in trigger:
                if button not in gun["buttons"]:
                    return None
            return trigger
        # Single button must be available
        if trigger not in gun["buttons"]:
            return None
        return trigger

    @staticmethod
    def __getPadMinMaxAxis(devicePath: str, axisCode: int) -> tuple[int, int]:
        """Get the minimum and maximum values for a specific axis on a controller.

        Args:
            devicePath (str): Path to the controller device (e.g., /dev/input/event0)
            axisCode (int): The Linux input event code for the axis

        Returns:
            tuple: (min_value, max_value) for the axis, or (0, 0) if not found

        """
        # Validate input parameters
        if not devicePath or not isinstance(devicePath, str):
            eslog.warning(f"Invalid device path provided: {devicePath}")
            return 0, 0

        if not isinstance(axisCode, int):
            eslog.warning(f"Invalid axis code provided: {axisCode}")
            return 0, 0

        try:
            # Check if the device path exists before attempting to open it
            device_path_obj = Path(devicePath)
            if not device_path_obj.exists():
                eslog.warning(f"Device path {devicePath} does not exist")
                return 0, 0

            # Check if the device path is accessible
            if not os.access(devicePath, os.R_OK):
                eslog.warning(f"Device path {devicePath} is not readable")
                return 0, 0

            device = InputDevice(devicePath)
            capabilities = device.capabilities(verbose=False)

            # Check if EV_ABS (3) is present in capabilities
            if 3 in capabilities:
                abs_events = capabilities[3]  # List of tuples (abs_code, val)
                for abs_info in abs_events:
                    # Ensure abs_info is a tuple with two elements
                    if isinstance(abs_info, tuple) and len(abs_info) == 2:
                        abs_code, val = abs_info
                        if abs_code == axisCode:
                            return val.min, val.max  # type: ignore
        except PermissionError as e:
            # Log permission denied error
            eslog.warning(f"Permission denied accessing {devicePath}: {e}")
            return 0, 0
        except FileNotFoundError as e:
            # Log device not found error
            eslog.warning(f"Device not found at {devicePath}: {e}")
            return 0, 0
        except OSError as e:
            # Handle other OS-related errors (like device busy, etc.)
            eslog.warning(f"OS error accessing device {devicePath}: {e}")
            return 0, 0
        except Exception as e:
            # Log any other unexpected errors
            eslog.warning(f"Unexpected error reading axis info from {devicePath}: {e}")
            return 0, 0

        return 0, 0  # Default values if axis not found

    @staticmethod
    def __getPadMinMaxAxisForKeys(min_val: int, max_val: int) -> tuple[float, float]:
        """Calculate adjusted axis range for keyboard key simulation.

        When using analog sticks to simulate key presses (rather than mouse movement),
        we want to use only the middle 50% of the axis range to provide better
        control and avoid accidental key presses from small stick movements.

        Args:
            min_val (int): Original minimum axis value
            max_val (int): Original maximum axis value

        Returns:
            tuple: (adjusted_min, adjusted_max) values for key simulation

        """
        valrange = (max_val - min_val) / 2  # Range for each side of center
        adjusted_min = min_val + valrange / 2  # 25% in from minimum
        adjusted_max = max_val - valrange / 2  # 25% in from maximum
        return adjusted_min, adjusted_max
