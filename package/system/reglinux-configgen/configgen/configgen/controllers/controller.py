"""
Controller class and related functions for managing game controller configurations.
Provides functionality to generate SDL game controller configuration strings.
"""
from typing import Dict, Optional, Any
from dataclasses import dataclass, field

from utils.logger import get_logger
eslog = get_logger(__name__)

@dataclass
class Input:
    """Represents a single input (button, axis, or hat) on a game controller."""
    name: str
    type: str
    id: str
    value: str
    code: Optional[int] = None

    @classmethod
    def from_sdl_mapping(cls, sdl_key: str, sdl_value: str) -> Optional['Input']:
        """
        Factory method to create an Input instance from SDL controller mapping string.

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
            parts = sdl_value[1:].split('.')  # Remove 'h' and split
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

@dataclass
class Controller:
    guid: str
    name: str = ""
    inputs: Dict[str, Any] = field(default_factory=dict)
    type: str = ""
    index: str = "-1"
    dev: Optional[Any] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Controller":
        return cls(
            guid=data.get("guid", ""),
            name=data.get("name", ""),
            inputs=data.get("inputs", {}),
            type=data.get("type", ""),
            index=str(data.get("index", "-1")),
            dev=data.get("dev", None)
        )

    def generateSDLGameDBLine(self):
        return _generateSdlGameControllerConfig(self)

def _generateSdlGameControllerConfig(controller: Controller) -> str:
    config = [controller.guid, controller.name]
    for key, value in controller.inputs.items():
        if isinstance(value, Input):
            config.append(f"{key}:{value.value}")
        else:
            config.append(f"{key}:{value}")
    config.append('')
    return ','.join(config)

def generateSdlGameControllerConfig(controllers: Dict) -> str:
    """
    Generate SDL game controller configuration for multiple controllers.

    Args:
        controllers: Dictionary of Controller instances

    Returns:
        Newline-separated configuration strings
    """
    return "\n".join(controller.generateSDLGameDBLine()
                    for controller in controllers.values())


def writeSDLGameDBAllControllers(controllers: Dict,
                               outputFile: str = "/tmp/gamecontrollerdb.txt") -> str:
    """
    Write SDL game controller configuration to a file.

    Args:
        controllers: Dictionary of Controller instances
        output_file: Path to output file

    Returns:
        Path to the output file
    """
    with open(outputFile, "w") as text_file:
        text_file.write(generateSdlGameControllerConfig(controllers))
    return outputFile
