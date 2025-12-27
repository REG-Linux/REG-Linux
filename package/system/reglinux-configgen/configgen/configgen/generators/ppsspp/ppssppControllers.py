from typing import Any

from configgen.settings import UnixSettings

from .ppssppConfig import PPSSPP_CONTROLS_SOURCE_PATH

# This configgen is based on PPSSPP 1.5.4.
# Therefore, all code/github references are valid at this version, and may not be valid with later updates

# PPSSPP internal "NKCodes" https://github.com/hrydgard/ppsspp/blob/master/Common/Input/KeyCodes.h

# Hotkeys - %d-%d
# DEVICE_ID_KEYBOARD = 1
# NKCODE_F1 = 131,
# NKCODE_F2 = 132,
# NKCODE_F3 = 133,
# NKCODE_F4 = 134,
# NKCODE_F5 = 135,
# NKCODE_F6 = 136,
# NKCODE_F7 = 137,
# NKCODE_F8 = 138,
# NKCODE_F9 = 139,
# NKCODE_F10 = 140,
# NKCODE_F11 = 141,
# NKCODE_F12 = 142,

# Will later be used to convert SDL input ids
NKCODE_BUTTON_1 = 188
NKCODE_BUTTON_2 = 189
NKCODE_BUTTON_3 = 190
NKCODE_BUTTON_4 = 191
NKCODE_BUTTON_5 = 192
NKCODE_BUTTON_6 = 193
NKCODE_BUTTON_7 = 194
NKCODE_BUTTON_8 = 195
NKCODE_BUTTON_9 = 196
NKCODE_BUTTON_10 = 197
NKCODE_BUTTON_11 = 198
NKCODE_BUTTON_12 = 199
NKCODE_BUTTON_13 = 200
NKCODE_BUTTON_14 = 201
NKCODE_BUTTON_15 = 202
NKCODE_BUTTON_16 = 203
NKCODE_BACK = 4
JOYSTICK_AXIS_X = 0
JOYSTICK_AXIS_Y = 1
JOYSTICK_AXIS_HAT_X = 15
JOYSTICK_AXIS_HAT_Y = 16
JOYSTICK_AXIS_Z = 11
JOYSTICK_AXIS_RZ = 14
JOYSTICK_AXIS_LTRIGGER = 17
JOYSTICK_AXIS_RTRIGGER = 18
NKCODE_DPAD_UP = 19
NKCODE_DPAD_DOWN = 20
NKCODE_DPAD_LEFT = 21
NKCODE_DPAD_RIGHT = 22

# PPSSPP defined an offset for axis
AXIS_BIND_NKCODE_START = 4000

DEVICE_ID_PAD_0 = 10
# SDL2 input ids conversion table to NKCodes
# See https://hg.libsdl.org/SDL/file/e12c38730512/include/SDL_gamecontroller.h#l262
sdlNameToNKCode = {
    "b": NKCODE_BUTTON_2,  # A
    "a": NKCODE_BUTTON_3,  # B
    "y": NKCODE_BUTTON_4,  # X
    "x": NKCODE_BUTTON_1,  # Y
    "back": NKCODE_BUTTON_9,  # SELECT/BACK
    "start": NKCODE_BUTTON_10,  # START
    "leftshoulder": NKCODE_BUTTON_6,  # L
    "rightshoulder": NKCODE_BUTTON_5,  # R
    "dpup": NKCODE_DPAD_UP,
    "dpdown": NKCODE_DPAD_DOWN,
    "dpleft": NKCODE_DPAD_LEFT,
    "dpright": NKCODE_DPAD_RIGHT,
}

SDLHatMap = {
    "dpup": NKCODE_DPAD_UP,
    "dpdown": NKCODE_DPAD_DOWN,
    "dpleft": NKCODE_DPAD_LEFT,
    "dpright": NKCODE_DPAD_RIGHT,
}

SDLJoyAxisMap = {
    "0": JOYSTICK_AXIS_X,
    "1": JOYSTICK_AXIS_Y,
    "2": JOYSTICK_AXIS_Z,
    "3": JOYSTICK_AXIS_RZ,
    "4": JOYSTICK_AXIS_LTRIGGER,
    "5": JOYSTICK_AXIS_RTRIGGER,
}

ppssppMapping = {
    "a": {"button": "Circle"},
    "b": {"button": "Cross"},
    "x": {"button": "Triangle"},
    "y": {"button": "Square"},
    "start": {"button": "Start"},
    "back": {"button": "Select"},
    "leftshoulder": {"button": "L"},
    "rightshoulder": {"button": "R"},
    "leftx": {"axis": "An.Left"},
    "lefty": {"axis": "An.Up"},
    "rightx": {"axis": "RightAn.Left"},
    "righty": {"axis": "RightAn.Up"},
    # The DPAD can be an axis (for gpio sticks for example) or a hat
    "dpup": {"hat": "Up", "axis": "Up", "button": "Up"},
    "dpdown": {"hat": "Down", "axis": "Down", "button": "Down"},
    "dpleft": {"hat": "Left", "axis": "Left", "button": "Left"},
    "dpright": {"hat": "Right", "axis": "Right", "button": "Right"},
    # Need to add pseudo inputs as PPSSPP doesn't manually invert axises
    "joystick1right": {"axis": "An.Right"},
    "joystick1down": {"axis": "An.Down"},
    "joystick2right": {"axis": "RightAn.Right"},
    "joystick2down": {"axis": "RightAn.Down"},
}


# Create the controller configuration file
def setControllerConfig(controller: Any) -> None:
    ppssppControllers = UnixSettings(PPSSPP_CONTROLS_SOURCE_PATH)

    ppssppControllers.ensure_section("ControlMapping")

    # Parse controller inputs
    for index in controller.inputs:
        input = controller.inputs[index]
        if (
            input.name not in ppssppMapping
            or input.type not in ppssppMapping[input.name]
        ):
            continue

        var = ppssppMapping[input.name][input.type]
        # Convert controller.index to integer
        padnum = int(controller.index)

        if input.type == "button":
            pspcode = sdlNameToNKCode[input.name]
            val = f"{DEVICE_ID_PAD_0 + padnum}-{pspcode}"
            val = optionValue(ppssppControllers, "ControlMapping", var, val)
            ppssppControllers.set("ControlMapping", var, val)

        elif input.type == "axis":
            # Get the axis code
            nkAxisId = SDLJoyAxisMap[input.id]
            # Apply the magic axis formula
            pspcode = axisToCode(nkAxisId, int(input.value))
            val = f"{DEVICE_ID_PAD_0 + padnum}-{pspcode}"
            val = optionValue(ppssppControllers, "ControlMapping", var, val)
            ppssppControllers.set("ControlMapping", var, val)

            # Skip the rest if it's an axis dpad
            if input.name in ["up", "down", "left", "right"]:
                continue
            # Also need to do the opposite direction manually. The input.id is the same as up/left, but the direction is opposite
            if input.name == "lefty":
                var = ppssppMapping["joystick1down"][input.type]
            elif input.name == "leftx":
                var = ppssppMapping["joystick1right"][input.type]
            elif input.name == "righty":
                var = ppssppMapping["joystick2down"][input.type]
            elif input.name == "rightx":
                var = ppssppMapping["joystick2right"][input.type]

            pspcode = axisToCode(nkAxisId, -int(input.value))
            val = f"{DEVICE_ID_PAD_0 + padnum}-{pspcode}"
            val = optionValue(ppssppControllers, "ControlMapping", var, val)
            ppssppControllers.set("ControlMapping", var, val)

        elif input.type == "hat" and input.name in SDLHatMap:
            var = ppssppMapping[input.name][input.type]
            pspcode = SDLHatMap[input.name]
            val = f"{DEVICE_ID_PAD_0 + padnum}-{pspcode}"
            val = optionValue(ppssppControllers, "ControlMapping", var, val)
            ppssppControllers.set("ControlMapping", var, val)

    # hotkey controls are called via evmapy.
    # configuring specific hotkey in ppsspp is not simple without patching
    ppssppControllers.set("ControlMapping", "Rewind", "1-131")
    ppssppControllers.set("ControlMapping", "Fast-forward", "1-132")
    ppssppControllers.set("ControlMapping", "Save State", "1-133")
    ppssppControllers.set("ControlMapping", "Load State", "1-134")
    ppssppControllers.set("ControlMapping", "Previous Slot", "1-135")
    ppssppControllers.set("ControlMapping", "Next Slot", "1-136")
    ppssppControllers.set("ControlMapping", "Screenshot", "1-137")
    ppssppControllers.set("ControlMapping", "Pause", "1-139")

    ppssppControllers.write()


def axisToCode(axisId: int, direction: int) -> int:
    if direction < 0:
        direction = 1
    else:
        direction = 0
    return AXIS_BIND_NKCODE_START + axisId * 2 + direction


# determine if the option already exists or not
def optionValue(config: Any, section: str, option: str, value: str) -> str:
    if config.has_option(section, option):
        return f"{config.get(section, option)},{value}"
    return value
