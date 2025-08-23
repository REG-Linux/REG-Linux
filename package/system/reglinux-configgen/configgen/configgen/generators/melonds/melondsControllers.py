def setMelondsControllers(melondsConfig, playersControllers):
    # Map controllers
    melonDSMapping = {
    "a":        "Joy_A",
    "b":        "Joy_B",
    "select":   "Joy_Select",
    "start":    "Joy_Start",
    "right":    "Joy_Right",
    "left":     "Joy_Left",
    "up":       "Joy_Up",
    "down":     "Joy_Down",
    "pagedown": "Joy_R",
    "pageup":   "Joy_L",
    "x":        "Joy_X",
    "y":        "Joy_Y"
    }

    val = -1
    for controller, pad in sorted(playersControllers.items()):
        # Only use Player 1 controls
        if pad.index != "1":
            continue

        # Handle controllers where guide and back buttons share the same code
        guide_equal_back = True if pad.inputs['guide'].value == pad.inputs['back'].value else False

        for index in pad.inputs:
            input = pad.inputs[index].sdl_to_linux_input_event(guide_equal_back)
            if input is None or input["name"] not in melonDSMapping:
                continue
            option = melonDSMapping[input["name"]]
            # Workaround - SDL numbers?
            val = input["id"]
            if val == "0":
                if option == "Joy_Up":
                    val = 257
                elif option == "Joy_Down":
                    val = 260
                elif option == "Joy_Left":
                    val = 264
                elif option == "Joy_Right":
                    val = 258
            melondsConfig.write(f"{option}={val}\n")
    # Always set ID to 0
    melondsConfig.write("JoystickID=0\n")
