"""Evmapy Manager Module for REG-Linux ConfigGen.

This module provides the high-level Evmapy manager that handles configuration
loading from emulator-specific modules and lifecycle management for the
native evmapy event handling implementation.

Acknowledgments:
    This implementation is based on the original evmapy project by kempniu.
    See: https://github.com/kempniu/evmapy

Key Responsibilities:
    - Load configurations from {emulator}_keys.py modules
    - Prepare device configurations as dictionaries (zero file I/O)
    - Manage EvmapyNative lifecycle (start/stop)
    - Handle light gun and controller mappings

Architecture:
    The Evmapy class uses EvmapyNative internally for direct Python-based
    event handling, eliminating the dependency on external evmapy binaries.

Example:
    from configgen.controllers.evmapy import Evmapy

    # Start evmapy - loads config from pcsx2_keys.py
    Evmapy.start(system, "pcsx2", "pcsx2", rom, controllers, guns)

    # Stop evmapy when emulator exits
    Evmapy.stop()

"""

from __future__ import annotations

import importlib.util
import threading
from pathlib import Path
from typing import Any

from evdev import InputDevice

from configgen.controllers.evmapy.event_handler import EvmapyNative
from configgen.controllers.mouse import mouseButtonToCode
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


class Evmapy:
    """Event Mapper class for handling gamepad to keyboard/mouse input mapping.

    This class manages the process that maps gamepad inputs to keyboard events,
    allowing controllers to be used with games that expect keyboard input.

    Uses EvmapyNative for direct Python-based event handling with:
        - Zero file I/O: Configurations loaded from Python modules
        - Minimal latency: Optimized event loop with 1ms response time
        - Thread-safe state management via threading.Event

    Attributes:
        __started_event: Thread-safe flag tracking evmapy state
        __native: EvmapyNative instance for event processing

    Example:
        # Start evmapy for PS2 emulation
        Evmapy.start(system, "pcsx2", "pcsx2", rom, controllers, [])

        # Stop when emulator exits
        Evmapy.stop()

    """

    # Track whether the evmapy process has been started
    # Using threading.Event for thread-safe state management
    __started_event = threading.Event()

    # Native evmapy instance
    __native: EvmapyNative | None = None

    @staticmethod
    def start(
        system: Any,
        emulator: str,
        core: str,
        rom: str,
        players_controllers: dict[str, Any],
        guns: dict[str, Any] | list[dict[str, Any]],
    ) -> None:
        """Start the evmapy event mapping system.

        Loads configuration from the emulator's {emulator}_keys.py module,
        prepares device configurations, and starts the native event handler.

        Args:
            system: The game system object (e.g., PS2, SNES, NES)
            emulator: The emulator name (e.g., "pcsx2", "snes9x")
            core: The emulator core name (e.g., "pcsx2", "snes9x")
            rom: Path to the ROM file or directory
            players_controllers: Dictionary mapping player numbers (1, 2, ...)
                                 to controller objects with dev, inputs, etc.
            guns: Light gun configurations - either dict or list format:
                  dict: {1: {"node": "/dev/event5", "buttons": [...]}}
                  list: [{"node": "/dev/event5", "buttons": [...]}]

        Raises:
            ImportError: If emulator's _keys module is not found

        Note:
            This method runs in a background thread to avoid blocking
            emulator startup. Event processing continues until stop() is called.

        Example:
            Evmapy.start(
                system=ps2_system,
                emulator="pcsx2",
                core="pcsx2",
                rom="/roms/ps2/game.iso",
                players_controllers={1: player1},
                guns=[]
            )

        """
        # Prepare configs and get device configurations as dictionaries
        device_configs = Evmapy.__prepare(
            system, emulator, core, rom, players_controllers, guns
        )

        # Don't start evmapy if no configuration was found
        if not device_configs:
            eslog.debug(f"Evmapy not started: no configuration for emulator={emulator}")
            return

        # Start evmapy native implementation
        Evmapy.__started_event.set()
        Evmapy.__native = EvmapyNative()

        # Load configurations directly from dictionaries (no file I/O)
        for device_name, config_data in device_configs.items():
            Evmapy.__native.load_config_dict(device_name, config_data)

        Evmapy.__native.start()
        eslog.info("Evmapy started (native mode)")

    @staticmethod
    def stop() -> None:
        """Stop the evmapy event mapping system and release resources.

        Gracefully stops the event processing threads, closes input devices,
        and releases the uinput device. Safe to call multiple times.

        Note:
            This method blocks until all background threads have terminated
            (with a 2-second timeout per thread).

        Example:
            # Stop evmapy after emulator exits
            Evmapy.stop()

        """
        if Evmapy.__started_event.is_set():
            Evmapy.__started_event.clear()
            if Evmapy.__native:
                Evmapy.__native.stop()
                Evmapy.__native = None
            eslog.info("Evmapy stopped")

    @staticmethod
    def __prepare(
        system: Any,
        emulator: str,
        core: str,
        rom: str,
        players_controllers: dict[str, Any],
        guns: dict[str, Any] | list[dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Prepare evmapy configuration from generator module.

        Loads configuration from the emulator's {emulator}_keys.py module and
        generates device configurations as dictionaries for direct loading
        into EvmapyNative (zero file I/O).

        Configuration Structure:
            - actions_player1: Button/axis mappings for player 1
            - actions_player2: Button/axis mappings for player 2 (optional)
            - actions_gun1: Light gun mappings for gun 1 (optional)
            - actions_gun2: Light gun mappings for gun 2 (optional)

        Args:
            system: The game system object
            emulator: The emulator name (used to load {emulator}_keys.py)
            core: The emulator core name (unused, kept for API compatibility)
            rom: ROM path (unused, kept for API compatibility)
            players_controllers: Player controller configurations
            guns: Light gun configurations

        Returns:
            Dictionary mapping device names to configuration dictionaries:
            {
                "event0": {"buttons": [...], "axes": [...], "actions": [...]},
                "event5": {"buttons": [...], "axes": [], "actions": [...]}
            }

        Note:
            Returns empty dict if:
            - Emulator's _keys module is not found
            - _keys module lacks get_config() function
            - Configuration is empty

        """
        device_configs: dict[str, dict[str, Any]] = {}

        # Convert emulator name to module name (hyphens to underscores)
        # e.g., "sonic-mania" -> "sonic_mania", "dxx-rebirth" -> "dxx_rebirth"
        # e.g., "fallout1-ce" -> "fallout1_ce", "fallout2-ce" -> "fallout2_ce"
        module_name = emulator.replace("-", "_")

        # Load configuration from _keys.py file directly using importlib.util
        # This avoids executing __init__.py which may have failing dependencies
        try:
            keys_module_path = (
                Path(__file__).parent.parent.parent
                / "generators"
                / module_name
                / f"{module_name}_keys.py"
            )
            spec = importlib.util.spec_from_file_location(
                f"{module_name}_keys", keys_module_path
            )
            if spec and spec.loader:
                keys_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(keys_module)
                if hasattr(keys_module, "get_config"):
                    padActionConfig: dict[str, Any] = keys_module.get_config()
                    eslog.debug(f"evmapy loaded config from {module_name}_keys module")
                else:
                    return device_configs
            else:
                return device_configs
        except (ImportError, ModuleNotFoundError, FileNotFoundError):
            eslog.debug(f"no evmapy config module found for emulator={emulator}")
            return device_configs

        # Configure light guns
        if isinstance(guns, dict):
            guns_enum = enumerate(guns.items(), start=1)
        else:
            guns_enum = enumerate(guns, start=1)

        for item in guns_enum:
            if isinstance(guns, dict):
                ngun, (_, gun) = item
                if not isinstance(gun, dict):
                    continue
                gun_node = gun["node"]
                gun_buttons = gun["buttons"]
            else:
                ngun, gun = item
                if not isinstance(gun, dict):
                    continue
                gun_node = gun["node"]
                gun_buttons = gun["buttons"]

            gun_action_key = "actions_gun" + str(ngun)
            if gun_action_key in padActionConfig:
                gun_device_name = Path(gun_node).name
                padConfig: dict[str, Any] = {
                    "buttons": [],
                    "axes": [],
                    "actions": [],
                    "grab": False,
                }

                for button in gun_buttons:
                    padConfig["buttons"].append(
                        {"name": button, "code": mouseButtonToCode(button)},
                    )

                gun_actions: list[dict[str, Any]] = padActionConfig[gun_action_key]
                for action in gun_actions:
                    if "trigger" in action and "type" in action and "target" in action:
                        guntrigger = Evmapy.__getGunTrigger(
                            action["trigger"],
                            gun,
                        )
                        if guntrigger:
                            newaction: dict[str, Any] = action.copy()
                            newaction.pop("description", None)
                            newaction["trigger"] = guntrigger
                            padConfig["actions"].append(newaction)

                device_configs[gun_device_name] = padConfig

        # Configure each player's controller
        for nplayer, (_, pad) in enumerate(
            sorted(players_controllers.items()),
            start=1,
        ):
            player_action_key = "actions_player" + str(nplayer)
            if player_action_key in padActionConfig:
                pad_device_name = Path(pad.dev).name
                padConfig = {
                    "axes": [],
                    "buttons": [],
                    "grab": False,
                }

                # Log mouse actions for this player
                mouse_actions = [
                    a
                    for a in padActionConfig[player_action_key]
                    if a.get("type") == "mouse"
                ]
                if mouse_actions:
                    mouse_triggers = [a.get("trigger") for a in mouse_actions]
                    eslog.info(
                        f"Evmapy: Mouse mapped to {', '.join(mouse_triggers)} on player {nplayer}"
                    )

                absbasex_positive = True
                absbasey_positive = True

                known_buttons_names: dict[str, Any] = {}
                known_buttons_codes: dict[int, str] = {}
                known_buttons_alias: dict[str, str] = {}
                known_axes_codes: dict[int, bool] = {}

                guide_equal_back = pad.inputs["guide"].value == pad.inputs["back"].value

                for index in pad.inputs:
                    input_obj = pad.inputs[index].sdl_to_linux_input_event(
                        guide_equal_back,
                    )
                    if input_obj is None:
                        continue

                    if input_obj["type"] == "button":
                        if input_obj["code"] is not None:
                            if input_obj["code"] not in known_buttons_codes:
                                known_buttons_names[input_obj["name"]] = True
                                known_buttons_codes[input_obj["code"]] = input_obj[
                                    "name"
                                ]
                                padConfig["buttons"].append(
                                    {
                                        "name": input_obj["name"],
                                        "code": int(input_obj["code"]),
                                    },
                                )
                            else:
                                known_buttons_alias[input_obj["name"]] = (
                                    known_buttons_codes[input_obj["code"]]
                                )

                    elif input_obj["type"] == "hat":
                        if int(input_obj["value"]) in [1, 2]:
                            if int(input_obj["value"]) == 1:
                                name = "X"
                                isYAsInt = 0
                            else:
                                name = "Y"
                                isYAsInt = 1

                            hat_name_min = "HAT" + input_obj["id"] + name + ":min"
                            hat_name_max = "HAT" + input_obj["id"] + name + ":max"
                            known_buttons_names[hat_name_min] = True
                            known_buttons_names[hat_name_max] = True

                            padConfig["axes"].append(
                                {
                                    "name": "HAT" + input_obj["id"] + name,
                                    "code": int(input_obj["id"]) + 16 + isYAsInt,
                                    "min": -1,
                                    "max": 1,
                                },
                            )

                    elif (
                        input_obj["type"] == "axis"
                        and input_obj["code"] not in known_axes_codes
                    ):
                        known_axes_codes[input_obj["code"]] = True
                        axisId: str | None = None
                        axisName: str | None = None

                        if input_obj["name"] in [
                            "joystick1up",
                            "joystick1left",
                        ]:
                            axisId = "0"
                        elif input_obj["name"] in [
                            "joystick2up",
                            "joystick2left",
                        ]:
                            axisId = "1"

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
                            axisId = "BASE"
                            axisName = "Y"
                            if input_obj["name"] == "up":
                                absbasey_positive = int(input_obj["value"]) >= 0
                            else:
                                axisId = None
                        elif input_obj["name"] in ["left", "right"]:
                            axisId = "BASE"
                            axisName = "X"
                            if input_obj["name"] == "left":
                                absbasex_positive = int(input_obj["value"]) < 0
                            else:
                                axisId = None
                        else:
                            axisId = "_OTHERS_"
                            axisName = input_obj["name"]

                        if (
                            (axisId in ["0", "1", "BASE"] and axisName in ["X", "Y"])
                            or axisId == "_OTHERS_"
                        ) and input_obj["code"] is not None:
                            axisMin, axisMax = Evmapy.__getPadMinMaxAxis(
                                pad.dev,
                                int(input_obj["code"]),
                            )

                            if axisId is not None and axisName is not None:
                                axis_base_name = "ABS" + axisId + axisName
                                known_buttons_names[axis_base_name + ":min"] = True
                                known_buttons_names[axis_base_name + ":max"] = True
                                known_buttons_names[axis_base_name + ":val"] = True

                                padConfig["axes"].append(
                                    {
                                        "name": axis_base_name,
                                        "code": int(input_obj["code"]),
                                        "min": axisMin,
                                        "max": axisMax,
                                    },
                                )

                padActionsPreDefined: list[dict[str, Any]] = padActionConfig[
                    player_action_key
                ]
                padActionsFiltered: list[dict[str, Any]] = []

                padActionsDefined: list[dict[str, Any]] = []
                for action in padActionsPreDefined:
                    if (
                        "type" in action
                        and action["type"] == "mouse"
                        and "target" not in action
                        and "trigger" in action
                    ):
                        if action["trigger"] == "joystick1":
                            newaction = action.copy()
                            newaction["trigger"] = "joystick1x"
                            newaction["target"] = "X"
                            padActionsDefined.append(newaction)

                            newaction = action.copy()
                            newaction["trigger"] = "joystick1y"
                            newaction["target"] = "Y"
                            padActionsDefined.append(newaction)

                        elif action["trigger"] == "joystick2":
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

                for action in padActionsDefined:
                    if "trigger" in action:
                        trigger = Evmapy.__trigger_mapper(
                            action["trigger"],
                            known_buttons_alias,
                            known_buttons_names,
                            absbasex_positive,
                            absbasey_positive,
                        )

                        if "mode" not in action:
                            mode = Evmapy.__trigger_mapper_mode(
                                action["trigger"],
                            )
                            if mode is not None:
                                action["mode"] = mode

                        action["trigger"] = trigger

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
                        elif trigger in known_buttons_names:
                            padActionsFiltered.append(action)
                        elif "ABS_OTHERS_" + trigger + ":max" in known_buttons_names:
                            action["trigger"] = "ABS_OTHERS_" + trigger + ":max"
                            padActionsFiltered.append(action)

                padConfig["actions"] = padActionsFiltered

                for action in padConfig["actions"]:
                    if "description" in action:
                        del action["description"]

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

                for axis in padConfig["axes"]:
                    axis_name = (
                        axis["name"]
                        if isinstance(axis, dict) and "name" in axis
                        else ""
                    )
                    axis_triggers = [
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

                device_configs[pad_device_name] = padConfig

        return device_configs

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
            known_buttons_alias: Button aliases for this controller
            known_buttons_names: Available button names for this controller (key existence checked only)
            absbasex_positive: Whether right is positive for base X axis
            absbasey_positive: Whether down is positive for base Y axis

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
            trigger: The trigger name to map
            known_buttons_alias: Button aliases for this controller
            known_buttons_names: Available button names for this controller (key existence checked only)
            absbasex_positive: Whether right is positive for base X axis
            absbasey_positive: Whether down is positive for base Y axis

        Returns:
            Mapped trigger name(s)

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
            The mode to use for this trigger type

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
            trigger: The trigger name

        Returns:
            "any" for analog mouse triggers, None otherwise

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
            gun: Gun configuration containing available buttons

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
            devicePath: Path to the controller device (e.g., /dev/input/event0)
            axisCode: The Linux input event code for the axis

        Returns:
            (min_value, max_value) for the axis, or (0, 0) if not found

        """
        # Validate input parameters
        if not devicePath or not isinstance(devicePath, str):
            eslog.debug(f"Invalid device path: {devicePath}")
            return 0, 0

        if not isinstance(axisCode, int):
            eslog.debug(f"Invalid axis code: {axisCode}")
            return 0, 0

        try:
            device_path_obj = Path(devicePath)
            if not device_path_obj.exists() or not __import__("os").access(
                devicePath, __import__("os").R_OK
            ):
                eslog.debug(f"Device {devicePath} not accessible")
                return 0, 0

            device = InputDevice(devicePath)
            capabilities = device.capabilities(verbose=False)

            if 3 in capabilities:
                abs_events = capabilities[3]
                for abs_info in abs_events:
                    if isinstance(abs_info, tuple) and len(abs_info) == 2:
                        abs_code, val = abs_info
                        if abs_code == axisCode:
                            return val.min, val.max
        except (PermissionError, FileNotFoundError, OSError) as e:
            eslog.debug(f"Device {devicePath} access error: {type(e).__name__}")
            return 0, 0
        except Exception as e:
            eslog.warning(f"Unexpected error reading axis from {devicePath}: {e}")
            return 0, 0

        return 0, 0

    @staticmethod
    def __getPadMinMaxAxisForKeys(min_val: int, max_val: int) -> tuple[float, float]:
        """Calculate adjusted axis range for keyboard key simulation.

        When using analog sticks to simulate key presses (rather than mouse movement),
        we want to use only the middle 50% of the axis range to provide better
        control and avoid accidental key presses from small stick movements.

        Args:
            min_val: Original minimum axis value
            max_val: Original maximum axis value

        Returns:
            (adjusted_min, adjusted_max) values for key simulation

        """
        valrange = (max_val - min_val) / 2  # Range for each side of center
        adjusted_min = min_val + valrange / 2  # 25% in from minimum
        adjusted_max = max_val - valrange / 2  # 25% in from maximum
        return adjusted_min, adjusted_max
