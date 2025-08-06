def setAzaharControllers(azaharConfig, playersControllers):
    # Pads
    azaharButtons = {
        "button_a":      "a",
        "button_b":      "b",
        "button_x":      "x",
        "button_y":      "y",
        "button_up":     "up",
        "button_down":   "down",
        "button_left":   "left",
        "button_right":  "right",
        "button_l":      "pageup",
        "button_r":      "pagedown",
        "button_start":  "start",
        "button_select": "select",
        "button_zl":     "l2",
        "button_zr":     "r2",
        "button_home":   "hotkey"
    }

    azaharAxis = {
        "circle_pad":    "joystick1",
        "c_stick":       "joystick2"
    }

    ## [CONTROLS]
    if not azaharConfig.has_section("Controls"):
        azaharConfig.add_section("Controls")

    # Options required to load the functions when the configuration file is created
    if not azaharConfig.has_option("Controls", "profiles\\size"):
        azaharConfig.set("Controls", "profile", 0)
        azaharConfig.set("Controls", "profile\\default", "true")
        azaharConfig.set("Controls", "profiles\\1\\name", "default")
        azaharConfig.set("Controls", "profiles\\1\\name\\default", "true")
        azaharConfig.set("Controls", "profiles\\size", 1)

    for index in playersControllers :
        controller = playersControllers[index]
        # We only care about player 1
        if controller.index != "1":
            continue
        for x in azaharButtons:
            azaharConfig.set("Controls", "profiles\\1\\" + x, f'"{setButton(azaharButtons[x], controller.guid, controller.inputs)}"')
            for x in azaharAxis:
                azaharConfig.set("Controls", "profiles\\1\\" + x, f'"{setAxis(azaharAxis[x], controller.guid, controller.inputs)}"')
        break

@staticmethod
def setButton(key, padGuid, padInputs):
    # It would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
    if key in padInputs:
        input = padInputs[key]
        if input.type == "button":
            return ("button:{},guid:{},engine:sdl").format(input.id, padGuid)
        elif input.type == "hat":
            return ("engine:sdl,guid:{},hat:{},direction:{}").format(padGuid, input.id, hatdirectionvalue(input.value))
        elif input.type == "axis":
            # Untested, need to configure an axis as button / triggers buttons to be tested too
            return ("engine:sdl,guid:{},axis:{},direction:{},threshold:{}").format(padGuid, input.id, "+", 0.5)

@staticmethod
def setAxis(key, padGuid, padInputs):
    inputx = None
    inputy = None

    if key == "joystick1" and "joystick1left" in padInputs:
        inputx = padInputs["joystick1left"]
    elif key == "joystick2" and "joystick2left" in padInputs:
        inputx = padInputs["joystick2left"]

    if key == "joystick1" and "joystick1up" in padInputs:
        inputy = padInputs["joystick1up"]
    elif key == "joystick2" and "joystick2up" in padInputs:
        inputy = padInputs["joystick2up"]

    if inputx is None or inputy is None:
        return "";

    return ("axis_x:{},guid:{},axis_y:{},engine:sdl").format(inputx.id, padGuid, inputy.id)

@staticmethod
def hatdirectionvalue(value):
    if int(value) == 1:
        return "up"
    if int(value) == 4:
        return "down"
    if int(value) == 2:
        return "right"
    if int(value) == 8:
        return "left"
    return "unknown"


# Show mouse on screen
def getMouseMode(self, config, rom):
 if "azahar_screen_layout" in config and config["azahar_screen_layout"] == "1-false":
     return False
 else:
     return True
