from typing import Any

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


def setAzaharControllers(azaharConfig: Any, playersControllers: Any) -> None:
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
        "button_zl": "triggerleft",
        "button_zr": "triggerright",
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
        if controller.index != 0:
            continue
        for x in azaharButtons:
            azaharConfig.set(
                "Controls",
                "profiles\\1\\" + x,
                f'"{setButton(azaharButtons[x], controller.guid, controller.inputs)}"',
            )
        for x in azaharAxis:
            azaharConfig.set(
                "Controls",
                "profiles\\1\\" + x,
                f'"{setAxis(azaharAxis[x], controller.guid, controller.inputs)}"',
            )
        break


def setButton(key: str, padGuid: str, padInputs: Any) -> str:
    if key in padInputs:
        input_obj = padInputs[key]
        if input_obj.type == "button":
            return f"button:{input_obj.id},guid:{padGuid},engine:sdl"
        if input_obj.type == "hat":
            return f"engine:sdl,guid:{padGuid},hat:{input_obj.id},direction:{hatdirectionvalue(input_obj.id[-1])}"
    return ""  # Return empty string if key not found


def setAxis(key: str, padGuid: str, padInputs: Any) -> str:
    inputx, inputy = None, None
    if key == "leftx":
        inputx, inputy = padInputs.get("leftx"), padInputs.get("lefty")
    elif key == "rightx":
        inputx, inputy = padInputs.get("rightx"), padInputs.get("righty")

    if inputx is None or inputy is None:
        return ""

    return f"axis_x:{inputx.id},guid:{padGuid},axis_y:{inputy.id},engine:sdl"


@staticmethod
def hatdirectionvalue(value: str) -> str:
    if int(value) == 1:
        return "up"
    if int(value) == 4:
        return "down"
    if int(value) == 2:
        return "right"
    if int(value) == 8:
        return "left"
    return "unknown"


def getMouseMode(config: Any, rom: str) -> bool:
    return not (
        "azahar_screen_layout" in config and config["azahar_screen_layout"] == "1-false"
    )
