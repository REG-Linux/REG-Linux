from typing import Any

wheelTypeMapping = {"DrivingForce": "0", "DrivingForcePro": "1", "GTForce": "3"}


def isPlayingWithWheel(system: Any, wheels: Any) -> bool:
    return (
        system.isOptSet("use_wheels")
        and system.getOptBoolean("use_wheels")
        and len(wheels) > 0
    )


def useEmulatorWheels(playingWithWheel: Any, wheel_type: str) -> bool:
    if playingWithWheel is False:
        return False
    # the virtual type is the virtual wheel that use a physical wheel to manipulate the pad
    return wheel_type != "Virtual"


def getWheelType(metadata: Any, playingWithWheel: Any, config: Any) -> str:
    wheel_type = "Virtual"
    if playingWithWheel is False:
        return wheel_type
    if "wheel_type" in metadata:
        wheel_type = metadata["wheel_type"]
    if "pcsx2_wheel_type" in config:
        wheel_type = config["pcsx2_wheel_type"]
    if wheel_type not in wheelTypeMapping:
        wheel_type = "Virtual"
    return wheel_type


def input2wheel(input_param: Any, reversedAxis: bool = False) -> str:
    if input_param.type == "button":
        pcsx2_magic_button_offset = 21  # PCSX2/SDLInputSource.cpp : const u32 button = ev->button + std::size(s_sdl_button_names)
        return f"Button{int(input_param.id) + pcsx2_magic_button_offset}"
    if input_param.type == "hat":
        direction = "unknown"
        if input_param.value == "1":
            direction = "North"
        elif input_param.value == "2":
            direction = "East"
        elif input_param.value == "4":
            direction = "South"
        elif input_param.value == "8":
            direction = "West"
        return f"Hat{input_param.id}{direction}"
    if input_param.type == "axis":
        pcsx2_magic_axis_offset = 6  # PCSX2/SDLInputSource.cpp : const u32 axis = ev->axis + std::size(s_sdl_axis_names);
        if reversedAxis is None:
            return f"FullAxis{int(input_param.id) + pcsx2_magic_axis_offset}~"
        direction_sign = "-"
        if reversedAxis:
            direction_sign = "+"
        return f"{direction_sign}Axis{int(input_param.id) + pcsx2_magic_axis_offset}"
    return "Unknown"  # Default value for other input types
