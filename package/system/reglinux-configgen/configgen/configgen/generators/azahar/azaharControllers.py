def setAzaharControllers(azaharConfig, playersControllers):
    azaharButtons = {
        "button_a": "a", "button_b": "b", "button_x": "x", "button_y": "y",
        "button_up": "up", "button_down": "down", "button_left": "left", "button_right": "right",
        "button_l": "pageup", "button_r": "pagedown",
        "button_start": "start", "button_select": "select",
        "button_zl": "l2", "button_zr": "r2", "button_home": "hotkey"
    }

    azaharAxis = {"circle_pad": "joystick1", "c_stick": "joystick2"}

    azaharConfig.ensure_section("Controls")

    if not azaharConfig.has_option("Controls", "profiles\\size"):
        azaharConfig.set("Controls", "profile", 0)
        azaharConfig.set("Controls", "profile\\default", "true")
        azaharConfig.set("Controls", "profiles\\1\\name", "default")
        azaharConfig.set("Controls", "profiles\\1\\name\\default", "true")
        azaharConfig.set("Controls", "profiles\\size", 1)

    for index in playersControllers:
        controller = playersControllers[index]
        if controller.index != "1":
            continue
        for x in azaharButtons:
            azaharConfig.set("Controls", "profiles\\1\\" + x,
                             f'"{setButton(azaharButtons[x], controller.guid, controller.inputs)}"')
        for x in azaharAxis:
            azaharConfig.set("Controls", "profiles\\1\\" + x,
                             f'"{setAxis(azaharAxis[x], controller.guid, controller.inputs)}"')
        break


def setButton(key, padGuid, padInputs):
    if key in padInputs:
        input = padInputs[key]
        if input.type == "button":
            return f"button:{input.id},guid:{padGuid},engine:sdl"
        elif input.type == "hat":
            return f"engine:sdl,guid:{padGuid},hat:{input.id},direction:{hatdirectionvalue(input.value)}"
        elif input.type == "axis":
            return f"engine:sdl,guid:{padGuid},axis:{input.id},direction:+,threshold:0.5"


def setAxis(key, padGuid, padInputs):
    inputx, inputy = None, None
    if key == "joystick1":
        inputx, inputy = padInputs.get("joystick1left"), padInputs.get("joystick1up")
    elif key == "joystick2":
        inputx, inputy = padInputs.get("joystick2left"), padInputs.get("joystick2up")

    if inputx is None or inputy is None:
        return ""
    return f"axis_x:{inputx.id},guid:{padGuid},axis_y:{inputy.id},engine:sdl"


def hatdirectionvalue(value):
    return {1: "up", 4: "down", 2: "right", 8: "left"}.get(int(value), "unknown")


def getMouseMode(self, config, rom):
    return not ("azahar_screen_layout" in config and config["azahar_screen_layout"] == "1-false")
