from typing import Any

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


def generateControllerConfig(
    system: Any,
    playersControllers: Any,
    metadata: Any,
    wheels: Any,
    rom: str,
    guns: Any,
) -> None:
    """Create the controller configuration file based on the system and game settings.

    Args:
        system: System configuration object
        playersControllers: Player controllers configuration
        metadata: Game metadata
        wheels: Wheel controllers
        rom: ROM file path
        guns: Light gun controllers

    """
    if system.name == "wii":
        from .wiiControllers import generateControllerConfig_wii

        generateControllerConfig_wii(
            system, playersControllers, metadata, wheels, rom, guns,
        )
    elif system.name == "gamecube":
        from .gamecubeControllers import generateControllerConfig_gamecube

        used_wheels: dict[str, Any] = {}
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
            system, playersControllers, used_wheels, rom,
        )  # Pass ROM name to allow for per ROM configuration
    else:
        raise ValueError(f"Invalid system name: '{system.name}'")
