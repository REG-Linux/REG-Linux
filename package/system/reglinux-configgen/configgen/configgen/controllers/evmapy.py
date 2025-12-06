"""
Event Mapper (Evmapy) Module

This module provides functionality to map gamepad/controller inputs to keyboard events
for game emulation systems. It handles the configuration and management of input
mapping between physical controllers and virtual keyboard/mouse events.

The main purpose is to allow gamepads to control games that expect keyboard input
by translating gamepad button presses and analog stick movements into corresponding
keyboard key presses or mouse movements.
"""

from subprocess import call
from json import load, dumps
from os import path
import os
from evdev import InputDevice
from .mouse import mouseButtonToCode
from utils.logger import get_logger

eslog = get_logger(__name__)


class Evmapy:
    """
    Event Mapper class for handling gamepad to keyboard/mouse input mapping.

    This class manages the process that maps gamepad inputs to keyboard events,
    allowing controllers to be used with games that expect keyboard input.
    """

    # Track whether the evmapy process has been started
    __started = False

    @staticmethod
    def start(system, emulator, core, rom, playersControllers, guns):
        """
        Start the evmapy process with the given configuration.

        Args:
            system (str): The game system name (e.g., 'snes', 'nes', 'arcade')
            emulator (str): The emulator being used
            core (str): The emulator core being used
            rom (str): Path to the ROM file or directory
            playersControllers (dict): Dictionary mapping player numbers to controller objects
            guns (dict): Dictionary of light gun configurations

        Returns:
            None
        """
        if Evmapy.__prepare(system, emulator, core, rom, playersControllers, guns):
            Evmapy.__started = True
            call(["system-evmapy", "start"])

    @staticmethod
    def stop():
        """
        Stop the evmapy process if it's currently running.

        Returns:
            None
        """
        if Evmapy.__started:
            Evmapy.__started = False
            call(["system-evmapy", "stop"])

    @staticmethod
    def __prepare(system, emulator, core, rom, playersControllers, guns):
        """
        Prepare evmapy configuration files for the given system and controllers.

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
            playersControllers (dict): Dictionary mapping player numbers to controller objects
            guns (dict): Dictionary of light gun configurations

        Returns:
            bool: True if configuration was successfully prepared, False otherwise
        """
        # Search for configuration files in order of precedence
        for keysfile in [
            "{}.keys".format(rom),  # ROM-specific configuration
            "{}/padto.keys".format(rom),  # Configuration inside ROM directory
            # Commented out more specific configurations for now
            # "/userdata/system/configs/evmapy/{}.{}.{}.keys".format(system, emulator, core),
            # "/userdata/system/configs/evmapy/{}.{}.keys".format(system, emulator),
            "/userdata/system/configs/evmapy/{}.keys".format(
                system
            ),  # User system config
            # System-wide configurations
            # "/usr/share/evmapy/{}.{}.{}.keys".format(system, emulator, core),
            "/usr/share/evmapy/{}.{}.keys".format(
                system, emulator
            ),  # System+emulator config
            "/usr/share/evmapy/{}.keys".format(system),  # Default system config
        ]:
            # Check if configuration file exists and handle directory ROM case
            if path.exists(keysfile) and not (
                path.isdir(rom) and keysfile == "{}.keys".format(rom)
            ):
                eslog.debug(f"evmapy on {keysfile}")

                # Clear any existing evmapy configuration
                call(["system-evmapy", "clear"])

                # Load the pad action configuration from the keys file
                padActionConfig = load(open(keysfile))

                # Configure light guns
                ngun = 1
                for gun in guns:
                    gun_action_key = "actions_gun" + str(ngun)
                    if gun_action_key in padActionConfig:
                        # Generate configuration file path for this gun
                        configfile = "/var/run/evmapy/{}.json".format(
                            path.basename(guns[gun]["node"])
                        )
                        eslog.debug(
                            "config file for keysfile is {} (from {}) - gun".format(
                                configfile, keysfile
                            )
                        )

                        # Initialize gun configuration structure
                        padConfig = {}
                        padConfig["buttons"] = []
                        padConfig["axes"] = []
                        padConfig["actions"] = []

                        # Add gun buttons to configuration
                        for button in guns[gun]["buttons"]:
                            padConfig["buttons"].append(
                                {"name": button, "code": mouseButtonToCode(button)}
                            )
                        padConfig["grab"] = False

                        # Process gun actions from the configuration
                        for action in padActionConfig[gun_action_key]:
                            if (
                                "trigger" in action
                                and "type" in action
                                and "target" in action
                            ):
                                guntrigger = Evmapy.__getGunTrigger(
                                    action["trigger"], guns[gun]
                                )
                                if guntrigger:
                                    newaction = action.copy()
                                    # Remove description field as it's not needed in runtime config
                                    if "description" in newaction:
                                        del newaction["description"]
                                    newaction["trigger"] = guntrigger
                                    padConfig["actions"].append(newaction)

                        # Write gun configuration to file
                        with open(configfile, "w") as fd:
                            fd.write(dumps(padConfig, indent=4))
                    ngun += 1

                # Configure each player's controller
                nplayer = 1
                for playercontroller, pad in sorted(playersControllers.items()):
                    player_action_key = "actions_player" + str(nplayer)
                    if player_action_key in padActionConfig:
                        # Generate configuration file path for this controller
                        configfile = "/var/run/evmapy/{}.json".format(
                            path.basename(pad.dev)
                        )
                        eslog.debug(
                            "config file for keysfile is {} (from {})".format(
                                configfile, keysfile
                            )
                        )

                        # Initialize controller configuration structure
                        padConfig = {}
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
                        known_buttons_names = {}  # Buttons available on this controller
                        known_buttons_codes = {}  # Map button codes to names
                        known_buttons_alias = {}  # Alternative names for buttons
                        known_axes_codes = {}  # Axes available on this controller

                        # Handle controllers where guide and back buttons share the same code
                        guide_equal_back = (
                            True
                            if pad.inputs["guide"].value == pad.inputs["back"].value
                            else False
                        )

                        # Process all inputs from the controller
                        for index in pad.inputs:
                            input = pad.inputs[index].sdl_to_linux_input_event(
                                guide_equal_back
                            )
                            if input is None:
                                continue

                            if input["type"] == "button":
                                # Add button to configuration (avoid duplicates)
                                if input["code"] is not None:
                                    if input["code"] not in known_buttons_codes:
                                        known_buttons_names[input["name"]] = True
                                        known_buttons_codes[input["code"]] = input[
                                            "name"
                                        ]
                                        padConfig["buttons"].append(
                                            {
                                                "name": input["name"],
                                                "code": int(input["code"]),
                                            }
                                        )
                                    else:
                                        # Create alias for duplicate button codes
                                        known_buttons_alias[input["name"]] = (
                                            known_buttons_codes[input["code"]]
                                        )

                            elif input["type"] == "hat":
                                # Handle D-pad (hat) inputs - only process X and Y values once
                                if int(input["value"]) in [
                                    1,
                                    2,
                                ]:  # Don't duplicate values
                                    if int(input["value"]) == 1:
                                        name = "X"
                                        isYAsInt = 0
                                    else:
                                        name = "Y"
                                        isYAsInt = 1

                                    # Add hat axis min/max buttons
                                    hat_name_min = "HAT" + input["id"] + name + ":min"
                                    hat_name_max = "HAT" + input["id"] + name + ":max"
                                    known_buttons_names[hat_name_min] = True
                                    known_buttons_names[hat_name_max] = True

                                    padConfig["axes"].append(
                                        {
                                            "name": "HAT" + input["id"] + name,
                                            "code": int(input["id"])
                                            + 16
                                            + isYAsInt,  # 16 = HAT0X in linux/input.h
                                            "min": -1,
                                            "max": 1,
                                        }
                                    )

                            elif input["type"] == "axis":
                                # Handle analog stick and trigger inputs
                                if (
                                    input["code"] not in known_axes_codes
                                ):  # Avoid duplicates
                                    known_axes_codes[input["code"]] = True
                                    axisId = None
                                    axisName = None

                                    # Map axis inputs to standardized names
                                    if input["name"] in [
                                        "joystick1up",
                                        "joystick1left",
                                    ]:
                                        axisId = "0"  # Left analog stick
                                    elif input["name"] in [
                                        "joystick2up",
                                        "joystick2left",
                                    ]:
                                        axisId = "1"  # Right analog stick

                                    if input["name"] in ["joystick1up", "joystick2up"]:
                                        axisName = "Y"
                                    elif input["name"] in [
                                        "joystick1left",
                                        "joystick2left",
                                    ]:
                                        axisName = "X"
                                    elif input["name"] in ["up", "down"]:
                                        # D-pad implemented as axis
                                        axisId = "BASE"
                                        axisName = "Y"
                                        if input["name"] == "up":
                                            absbasey_positive = int(input["value"]) >= 0
                                        else:
                                            axisId = None  # Don't duplicate, configure only for 'up'
                                    elif input["name"] in ["left", "right"]:
                                        # D-pad implemented as axis
                                        axisId = "BASE"
                                        axisName = "X"
                                        if input["name"] == "left":
                                            absbasex_positive = int(input["value"]) < 0
                                        else:
                                            axisId = None  # Don't duplicate, configure only for 'left'
                                    else:
                                        # Other axes (triggers, etc.)
                                        axisId = "_OTHERS_"
                                        axisName = input["name"]

                                    # Add axis configuration if valid
                                    if (
                                        (
                                            axisId in ["0", "1", "BASE"]
                                            and axisName in ["X", "Y"]
                                        )
                                        or axisId == "_OTHERS_"
                                    ) and input["code"] is not None:
                                        axisMin, axisMax = Evmapy.__getPadMinMaxAxis(
                                            pad.dev, int(input["code"])
                                        )

                                        # Add axis virtual buttons (min, max, val)
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
                                                "code": int(input["code"]),
                                                "min": axisMin,
                                                "max": axisMax,
                                            }
                                        )

                        # Process actions from configuration file
                        padActionsPreDefined = padActionConfig[player_action_key]
                        padActionsFiltered = []

                        # Handle mouse events - expand joystick shortcuts to x/y components
                        padActionsDefined = []
                        for action in padActionsPreDefined:
                            if (
                                "type" in action
                                and action["type"] == "mouse"
                                and "target" not in action
                                and "trigger" in action
                            ):
                                if action["trigger"] == "joystick1":
                                    # Split joystick1 into x and y components
                                    newaction = action.copy()
                                    newaction["trigger"] = "joystick1x"
                                    newaction["target"] = "X"
                                    padActionsDefined.append(newaction)

                                    newaction = action.copy()
                                    newaction["trigger"] = "joystick1y"
                                    newaction["target"] = "Y"
                                    padActionsDefined.append(newaction)

                                elif action["trigger"] == "joystick2":
                                    # Split joystick2 into x and y components
                                    newaction = action.copy()
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
                                        action["trigger"]
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
                                        for i, val in enumerate(trigger):
                                            if (
                                                "ABS_OTHERS_" + val + ":max"
                                                in known_buttons_names
                                            ):
                                                action["trigger"][i] = (
                                                    "ABS_OTHERS_" + val + ":max"
                                                )
                                        padActionsFiltered.append(action)
                                else:
                                    # Single trigger validation
                                    if trigger in known_buttons_names:
                                        padActionsFiltered.append(action)
                                    elif (
                                        "ABS_OTHERS_" + trigger + ":max"
                                        in known_buttons_names
                                    ):
                                        action["trigger"] = (
                                            "ABS_OTHERS_" + action["trigger"] + ":max"
                                        )
                                        padActionsFiltered.append(action)

                        padConfig["actions"] = padActionsFiltered

                        # Clean up configuration by removing description fields
                        for action in padConfig["actions"]:
                            if "description" in action:
                                del action["description"]

                        # Optimize axis ranges based on usage
                        # Use full axis range for mouse, 50% range for keys
                        axis_for_mouse = {}
                        for action in padConfig["actions"]:
                            if "type" in action and action["type"] == "mouse":
                                if isinstance(action["trigger"], list):
                                    for x in action["trigger"]:
                                        axis_for_mouse[x] = True
                                else:
                                    axis_for_mouse[action["trigger"]] = True

                        # Adjust axis ranges for non-mouse actions
                        for axis in padConfig["axes"]:
                            axis_triggers = [
                                axis["name"] + ":val",
                                axis["name"] + ":min",
                                axis["name"] + ":max",
                            ]
                            if not any(
                                trigger in axis_for_mouse for trigger in axis_triggers
                            ):
                                min_val, max_val = Evmapy.__getPadMinMaxAxisForKeys(
                                    axis["min"], axis["max"]
                                )
                                axis["min"] = min_val
                                axis["max"] = max_val

                        # Write controller configuration to file
                        with open(configfile, "w") as fd:
                            fd.write(dumps(padConfig, indent=4))

                    nplayer += 1
                return True

        # No configuration file found
        eslog.debug(
            "no evmapy config file found for system={}, emulator={}".format(
                system, emulator
            )
        )
        return False

    @staticmethod
    def __trigger_mapper(
        trigger,
        known_buttons_alias,
        known_buttons_names,
        absbasex_positive,
        absbasey_positive,
    ):
        """
        Map evmapy trigger names to actual controller input names.

        This function translates generic trigger names (like 'up', 'joystick1left')
        to specific controller input names (like 'HAT0Y:max', 'ABS0X:min').

        Args:
            trigger: Either a string or list of trigger names to map
            known_buttons_alias (dict): Button aliases for this controller
            known_buttons_names (dict): Available button names for this controller
            absbasex_positive (bool): Whether right is positive for base X axis
            absbasey_positive (bool): Whether down is positive for base Y axis

        Returns:
            Mapped trigger name(s) - string or list depending on input
        """
        if isinstance(trigger, list):
            new_trigger = []
            for x in trigger:
                new_trigger.append(
                    Evmapy.__trigger_mapper_string(
                        x,
                        known_buttons_alias,
                        known_buttons_names,
                        absbasex_positive,
                        absbasey_positive,
                    )
                )
            return new_trigger
        return Evmapy.__trigger_mapper_string(
            trigger,
            known_buttons_alias,
            known_buttons_names,
            absbasex_positive,
            absbasey_positive,
        )

    @staticmethod
    def __trigger_mapper_string(
        trigger,
        known_buttons_alias,
        known_buttons_names,
        absbasex_positive,
        absbasey_positive,
    ):
        """
        Map a single trigger string to the appropriate controller input name.

        Args:
            trigger (str): The trigger name to map
            known_buttons_alias (dict): Button aliases for this controller
            known_buttons_names (dict): Available button names for this controller
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
    def __trigger_mapper_mode(trigger):
        """
        Determine the appropriate mode for a trigger.

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
    def __trigger_mapper_mode_string(trigger):
        """
        Determine the mode for a single trigger string.

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
    def __getGunTrigger(trigger, gun):
        """
        Validate that gun trigger(s) are available on the specified gun device.

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
        else:
            # Single button must be available
            if trigger not in gun["buttons"]:
                return None
            return trigger

    @staticmethod
    def __getPadMinMaxAxis(devicePath, axisCode):
        """
        Get the minimum and maximum values for a specific axis on a controller.

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
            if not path.exists(devicePath):
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
                            return val.min, val.max
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
    def __getPadMinMaxAxisForKeys(min_val, max_val):
        """
        Calculate adjusted axis range for keyboard key simulation.

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
