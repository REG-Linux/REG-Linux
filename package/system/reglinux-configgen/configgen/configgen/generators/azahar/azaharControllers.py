from typing import Any


def setAzaharControllers(azaharConfig: Any, playersControllers: Any) -> None:
    # Mapping from Azahar config keys to SDL controller input names
    azaharButtons = {
        "button_a": "a",
        "button_b": "b",
        "button_x": "x",
        "button_y": "y",
        "button_up": "dpup",
        "button_down": "dpdown",
        "button_left": "dpleft",
        "button_right": "dpright",
        "button_l": "leftshoulder",
        "button_r": "rightshoulder",
        "button_start": "start",
        "button_select": "back",
        "button_zl": "lefttrigger",
        "button_zr": "righttrigger",
        "button_home": "guide",
    }

    azaharAxis = {"circle_pad": "leftx", "c_stick": "rightx"}

    azaharConfig.ensure_section("Controls")

    if not azaharConfig.has_option("Controls", "profiles\\size"):
        azaharConfig.set("Controls", "profile", 0)
        azaharConfig.set("Controls", "profile\\default", "true")
        azaharConfig.set("Controls", "profiles\\1\\name", "default")
        azaharConfig.set("Controls", "profiles\\1\\name\\default", "true")
        azaharConfig.set("Controls", "profiles\\size", 1)

    for index in playersControllers:
        controller = playersControllers[index]
        # Player index is 1-based in playersControllers dict ("1", "2", etc.)
        # but controller.index is 0-based string ("0" = player 1, "1" = player 2, etc.)
        if controller.index not in (0, "0"):
            continue

        for x in azaharButtons:
            button_value = setButton(
                azaharButtons[x], controller.guid, controller.inputs
            )
            if button_value:
                azaharConfig.set(
                    "Controls",
                    "profiles\\1\\" + x,
                    f'"{button_value}"',
                )
                azaharConfig.set("Controls", "profiles\\1\\" + x + "\\default", "false")
        for x in azaharAxis:
            axis_value = setAxis(azaharAxis[x], controller.guid, controller.inputs)
            if axis_value:
                azaharConfig.set(
                    "Controls",
                    "profiles\\1\\" + x,
                    f'"{axis_value}"',
                )
                azaharConfig.set("Controls", "profiles\\1\\" + x + "\\default", "false")
        break


def setButton(key: str, padGuid: str, padInputs: Any) -> str:
    if key not in padInputs:
        return ""

    input_obj = padInputs[key]

    if input_obj.type == "button":
        return f"button:{input_obj.id},guid:{padGuid},engine:sdl"
    if input_obj.type == "hat":
        hat_id = input_obj.id
        direction = hatdirectionvalue(str(hat_id)[-1])
        return f"engine:sdl,guid:{padGuid},hat:{hat_id},direction:{direction}"

    return ""


def setAxis(key: str, padGuid: str, padInputs: Any) -> str:
    inputx, inputy = None, None
    if key == "leftx":
        inputx, inputy = padInputs.get("leftx"), padInputs.get("lefty")
    elif key == "rightx":
        inputx, inputy = padInputs.get("rightx"), padInputs.get("righty")

    if inputx is None or inputy is None:
        return ""

    return f"axis_x:{inputx.id},guid:{padGuid},axis_y:{inputy.id},engine:sdl"


def hatdirectionvalue(value: str) -> str:
    if value == "1":
        return "up"
    if value == "4":
        return "down"
    if value == "2":
        return "right"
    if value == "8":
        return "left"
    return "unknown"


def getMouseMode(config: Any, rom: str) -> bool:
    return not (
        "azahar_screen_layout" in config and config["azahar_screen_layout"] == "1-false"
    )
