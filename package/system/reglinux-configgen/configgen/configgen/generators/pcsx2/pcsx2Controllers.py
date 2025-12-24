wheelTypeMapping = {"DrivingForce": "0", "DrivingForcePro": "1", "GTForce": "3"}


def isPlayingWithWheel(system, wheels):
    return (
        system.isOptSet("use_wheels")
        and system.getOptBoolean("use_wheels")
        and len(wheels) > 0
    )


def useEmulatorWheels(playingWithWheel, wheel_type):
    if playingWithWheel is False:
        return False
    # the virtual type is the virtual wheel that use a physical wheel to manipulate the pad
    return wheel_type != "Virtual"


def getWheelType(metadata, playingWithWheel, config):
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


def input2wheel(input, reversedAxis=False):
    if input.type == "button":
        pcsx2_magic_button_offset = 21  # PCSX2/SDLInputSource.cpp : const u32 button = ev->button + std::size(s_sdl_button_names)
        return f"Button{int(input.id) + pcsx2_magic_button_offset}"
    if input.type == "hat":
        dir = "unknown"
        if input.value == "1":
            dir = "North"
        elif input.value == "2":
            dir = "East"
        elif input.value == "4":
            dir = "South"
        elif input.value == "8":
            dir = "West"
        return f"Hat{input.id}{dir}"
    if input.type == "axis":
        pcsx2_magic_axis_offset = 6  # PCSX2/SDLInputSource.cpp : const u32 axis = ev->axis + std::size(s_sdl_axis_names);
        if reversedAxis is None:
            return "{}Axis{}~".format("Full", int(input.id) + pcsx2_magic_axis_offset)
        dir = "-"
        if reversedAxis:
            dir = "+"
        return f"{dir}Axis{int(input.id) + pcsx2_magic_axis_offset}"
