"""Controller class and related functions for managing game controller configurations.
Provides functionality to generate SDL game controller configuration strings.
"""

from dataclasses import dataclass, field
from typing import Any, Optional

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


@dataclass
class Input:
    """Represents a single input (button, axis, or hat) on a game controller."""

    name: str
    type: str
    id: str
    value: str
    code: int | None = None

    @classmethod
    def from_sdl_mapping(cls, sdl_key: str, sdl_value: str) -> Optional["Input"]:
        """Factory method to create an Input instance from SDL controller mapping string.

        Handles all SDL controller mapping types (buttons, axes, and hats) according to:
        https://github.com/gabomdq/SDL_GameControllerDB/blob/master/README.md#entries

        Args:
            sdl_key: SDL input name (e.g. "a", "b", "dpup")
            sdl_value: SDL mapping value in format:
                    - "bX" for buttons (X = button number)
                    - "aX" for axes (X = axis number)
                    - "hX.Y" for hats (X = hat number, Y = direction)

        Returns:
            Input object if mapping is valid, None otherwise

        Examples:
            >>> Input.from_sdl_mapping("a", "b0")      # Button 0 (A button)
            >>> Input.from_sdl_mapping("leftx", "a0")  # Axis 0 (Left X)
            >>> Input.from_sdl_mapping("dpup", "h0.1") # Hat 0 Up

        """
        # Validate input parameters
        if not sdl_key or not sdl_value:
            return None

        # Initialize default values
        input_type = "button"
        code_value = sdl_value

        # Parse based on SDL input prefix
        if sdl_value.startswith("a"):  # Axis input
            input_type = "axis"
            code_value = sdl_value[1:]  # Extract axis number

        elif sdl_value.startswith("h"):  # Hat input
            input_type = "hat"
            # SDL hat format: h<hat_number>.<direction>
            parts = sdl_value[1:].split(".")  # Remove 'h' and split
            sdl_value = parts[0] if parts else ""  # Hat number

        elif sdl_value.startswith("b"):  # Button input
            code_value = sdl_value[1:]  # Extract button number

        # Create Input instance
        return cls(
            name=sdl_key,
            type=input_type,
            id=code_value,  # Processed value (number without prefix)
            value=sdl_value,  # Original SDL mapping string
            code=int(code_value) if code_value.isdigit() else None,
            # Additional hat metadata could be stored here if needed
        )

    def sdl_to_linux_input_event(self, guide_equal_back: bool) -> dict[str, Any] | None:
        """Converts SDL input mapping to a Linux input event structure with complete metadata.

        Returns:
            A dictionary containing:
                - name: SDL input name (e.g. "a", "leftx")
                - type: Event type string (e.g. "button", "axis", "hat")
                - id: SDL numeric identifier (e.g. "0", "1")
                - value: Original SDL mapping string (e.g. "b0", "a1", "h0.1")
                - code: Linux event code (e.g. 304 for BTN_SOUTH)

        """
        # Linux event codes: https://github.com/torvalds/linux/blob/master/include/uapi/linux/input-event-codes.h
        sdl_to_linux = {
            # Buttons
            "a": ("a", 304),
            "b": ("b", 305),
            "x": ("x", 307),
            "y": ("y", 308),
            "back": ("select", 314),
            "start": ("start", 315),
            "guide": ("hotkey", 316),
            "leftshoulder": ("pageup", 310),
            "rightshoulder": ("pagedown", 311),
            "leftstick": ("l3", 317),
            "rightstick": ("r3", 318),
            # D-Pad
            "dpup": ("up", 544),
            "dpdown": ("down", 545),
            "dpleft": ("left", 546),
            "dpright": ("right", 547),
            # Axes
            "leftx": ("joystick1left", 0),
            "lefty": ("joystick1up", 1),
            "rightx": ("joystick2left", 3),
            "righty": ("joystick2up", 4),
            "triggerleft": ("l2", 2),
            "triggerright": ("r2", 5),
        }

        key = self.name.lower()
        if key in sdl_to_linux:
            ev_name, ev_code = sdl_to_linux[key]
            if key == "guide" and guide_equal_back:
                ev_code = sdl_to_linux["back"][1]
            return {
                "name": ev_name,
                "type": self.type,
                "id": self.id,
                "value": self.value,
                "code": ev_code,
            }

        return None


@dataclass
class Controller:
    guid: str
    name: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)  # type: ignore
    type: str = ""
    index: int = -1
    dev: Any | None = None
    nbaxes: int | None = 0
    nbbuttons: int | None = 0
    nbhats: int | None = 0

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Controller":
        return cls(
            guid=data.get("guid", ""),
            name=data.get("name", ""),
            inputs=data.get("inputs", {}),
            type=data.get("type", ""),
            index=data.get("index", -1),
            dev=data.get("dev"),
            nbaxes=data.get("nbaxes", 0),
            nbbuttons=data.get("nbbuttons", 0),
            nbhats=data.get("nbhats", 0),
        )

    def generate_sdl_game_db_line(self):
        return _generate_sdl_controller_config(self)


def _generate_sdl_controller_config(controller: Controller) -> str:
    config = [controller.guid, controller.name]
    for key, value in controller.inputs.items():
        if isinstance(value, Input):
            config.append(f"{key}:{value.value}")
        else:
            config.append(f"{key}:{value}")
    config.append("")
    return ",".join(config)


def generate_sdl_controller_config(controllers: dict[str, Any]) -> str:
    """Generate SDL game controller configuration for multiple controllers.

    Args:
        controllers: Dictionary of Controller instances

    Returns:
        Newline-separated configuration strings

    """
    return "\n".join(
        controller.generate_sdl_game_db_line() for controller in controllers.values()
    )


def write_sdl_db_all_controllers(
    controllers: dict[str, Any],
    outputFile: str = "/tmp/gamecontrollerdb.txt",
) -> str:
    """Write SDL game controller configuration to a file.

    Args:
        controllers: Dictionary of Controller instances
        output_file: Path to output file

    Returns:
        Path to the output file

    """
    # Using the walrus operator for assignment expressions
    config_str = generate_sdl_controller_config(controllers)
    with open(outputFile, "w") as text_file:
        text_file.write(config_str)
    return outputFile
