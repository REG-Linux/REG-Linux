from typing import Any

# pads
edenButtonsMapping = {
    "button_a": "a",
    "button_b": "b",
    "button_x": "x",
    "button_y": "y",
    "button_dup": "dpup",
    "button_ddown": "dpdown",
    "button_dleft": "dpleft",
    "button_dright": "dpright",
    "button_l": "leftshoulder",
    "button_r": "rightshoulder",
    "button_plus": "start",
    "button_minus": "back",
    "button_sl": "leftstick",
    "button_sr": "rightstick",
    "button_zl": "triggerleft",
    "button_zr": "triggerright",
    "button_lstick": "leftstick",
    "button_rstick": "rightstick",
    "button_home": "guide",
}

edenAxisMapping = {"lstick": "joystick1", "rstick": "joystick2"}


def setEdenControllers(edenConfig: Any, system: Any, playersControllers: Any) -> None:
    # controllers
    nplayer = 1
    for _, pad in sorted(playersControllers.items()):
        if system.isOptSet(f"p{nplayer - 1}_pad"):
            edenConfig.set(
                "Controls",
                f"player_{nplayer - 1}_type",
                system.config[f"p{nplayer}_pad"],
            )
        else:
            edenConfig.set("Controls", f"player_{nplayer - 1}_type", 0)
        edenConfig.set("Controls", f"player_{nplayer - 1}_type\\default", "false")

        for x in edenButtonsMapping:
            edenConfig.set(
                "Controls",
                "player_" + str(nplayer - 1) + "_" + x,
                f'"{setButton(edenButtonsMapping[x], pad.guid, pad.inputs, nplayer - 1)}"',
            )
        for x in edenAxisMapping:
            edenConfig.set(
                "Controls",
                "player_" + str(nplayer - 1) + "_" + x,
                f'"{setAxis(edenAxisMapping[x], pad.guid, pad.inputs, nplayer - 1)}"',
            )
        edenConfig.set(
            "Controls", "player_" + str(nplayer - 1) + "_motionleft", '"[empty]"',
        )
        edenConfig.set(
            "Controls", "player_" + str(nplayer - 1) + "_motionright", '"[empty]"',
        )
        edenConfig.set("Controls", "player_" + str(nplayer - 1) + "_connected", "true")
        edenConfig.set(
            "Controls",
            "player_" + str(nplayer - 1) + "_connected\\default",
            "false",
        )
        edenConfig.set(
            "Controls", "player_" + str(nplayer - 1) + "_vibration_enabled", "true",
        )
        edenConfig.set(
            "Controls",
            "player_" + str(nplayer - 1) + "_vibration_enabled\\default",
            "false",
        )
        nplayer += 1

    edenConfig.set("Controls", "vibration_enabled", "true")
    edenConfig.set("Controls", "vibration_enabled\\default", "false")

    for y in range(nplayer, 9):
        edenConfig.set("Controls", "player_" + str(y - 1) + "_connected", "false")
        edenConfig.set(
            "Controls", "player_" + str(y - 1) + "_connected\\default", "false",
        )


@staticmethod
def setButton(key: str, padGuid: str, padInputs: Any, port: int) -> str:
    # it would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
    if key in padInputs:
        input = padInputs[key]

        if input.type == "button":
            return f"engine:sdl,button:{input.id},guid:{padGuid},port:{port}"
        if input.type == "hat":
            return f"engine:sdl,hat:{input.id},direction:{hatdirectionvalue(input.value)},guid:{padGuid},port:{port}"
        if input.type == "axis":
            return f"engine:sdl,threshold:{0.5},axis:{input.id},guid:{padGuid},port:{port},invert:{'+'}"
    return ""


@staticmethod
def setAxis(key: str, padGuid: str, padInputs: Any, port: int) -> str:
    inputx = "0"
    inputy = "0"

    if key == "joystick1" and "joystick1left" in padInputs:
        inputx = padInputs["joystick1left"]
    elif key == "joystick2" and "joystick2left" in padInputs:
        inputx = padInputs["joystick2left"]

    if key == "joystick1" and "joystick1up" in padInputs:
        inputy = padInputs["joystick1up"]
    elif key == "joystick2" and "joystick2up" in padInputs:
        inputy = padInputs["joystick2up"]
    return f"engine:sdl,range:1.000000,deadzone:0.100000,invert_y:+,invert_x:+,offset_y:-0.000000,axis_y:{inputy},offset_x:-0.000000,axis_x:{inputx},guid:{padGuid},port:{port}"


@staticmethod
def hatdirectionvalue(value: str) -> str:
    if int(value) == 1:
        return "dpup"
    if int(value) == 4:
        return "dpdown"
    if int(value) == 2:
        return "dpright"
    if int(value) == 8:
        return "dpleft"
    return "unknown"
