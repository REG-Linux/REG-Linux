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


def setEdenControllers(edenConfig, system, playersControllers):
    # controllers
    nplayer = 1
    for playercontroller, pad in sorted(playersControllers.items()):
        if system.isOptSet("p{}_pad".format(nplayer - 1)):
            edenConfig.set(
                "Controls",
                "player_{}_type".format(nplayer - 1),
                system.config["p{}_pad".format(nplayer)],
            )
        else:
            edenConfig.set("Controls", "player_{}_type".format(nplayer - 1), 0)
        edenConfig.set(
            "Controls", "player_{}_type\\default".format(nplayer - 1), "false"
        )

        for x in edenButtonsMapping:
            edenConfig.set(
                "Controls",
                "player_" + str(nplayer - 1) + "_" + x,
                '"{}"'.format(
                    setButton(edenButtonsMapping[x], pad.guid, pad.inputs, nplayer - 1)
                ),
            )
        for x in edenAxisMapping:
            edenConfig.set(
                "Controls",
                "player_" + str(nplayer - 1) + "_" + x,
                '"{}"'.format(
                    setAxis(edenAxisMapping[x], pad.guid, pad.inputs, nplayer - 1)
                ),
            )
        edenConfig.set(
            "Controls", "player_" + str(nplayer - 1) + "_motionleft", '"[empty]"'
        )
        edenConfig.set(
            "Controls", "player_" + str(nplayer - 1) + "_motionright", '"[empty]"'
        )
        edenConfig.set("Controls", "player_" + str(nplayer - 1) + "_connected", "true")
        edenConfig.set(
            "Controls",
            "player_" + str(nplayer - 1) + "_connected\\default",
            "false",
        )
        edenConfig.set(
            "Controls", "player_" + str(nplayer - 1) + "_vibration_enabled", "true"
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
            "Controls", "player_" + str(y - 1) + "_connected\\default", "false"
        )


@staticmethod
def setButton(key, padGuid, padInputs, port):
    # it would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
    if key in padInputs:
        input = padInputs[key]

        if input.type == "button":
            return ("engine:sdl,button:{},guid:{},port:{}").format(
                input.id, padGuid, port
            )
        elif input.type == "hat":
            return ("engine:sdl,hat:{},direction:{},guid:{},port:{}").format(
                input.id,
                hatdirectionvalue(input.value),
                padGuid,
                port,
            )
        elif input.type == "axis":
            return ("engine:sdl,threshold:{},axis:{},guid:{},port:{},invert:{}").format(
                0.5, input.id, padGuid, port, "+"
            )
    return ""


@staticmethod
def setAxis(key, padGuid, padInputs, port):
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
    return (
        "engine:sdl,range:1.000000,deadzone:0.100000,invert_y:+,invert_x:+,offset_y:-0.000000,axis_y:{},offset_x:-0.000000,axis_x:{},guid:{},port:{}"
    ).format(inputy, inputx, padGuid, port)


@staticmethod
def hatdirectionvalue(value):
    if int(value) == 1:
        return "dpup"
    if int(value) == 4:
        return "dpdown"
    if int(value) == 2:
        return "dpright"
    if int(value) == 8:
        return "dpleft"
    else:
        return "unknown"
