def setControllerConfig(config, playersControllers, core):
    if core == "openbor4432":
        setupControllers(config, playersControllers, 32, False)
    elif core == "openbor7142":
        setupControllers(config, playersControllers, 64, True)
    else:
        setupControllers(config, playersControllers, 64, False)


def JoystickValue(key, pad, joy_max_inputs, new_axis_vals, invertAxis=False):
    if key not in pad.inputs:
        return 0

    value = 0
    input = pad.inputs[key]

    if input.type == "button":
        value = 1 + (int(pad.index)) * joy_max_inputs + int(input.id)

    elif input.type == "hat":
        input.id = input.id[-1]
        if new_axis_vals:
            hatfirst = 1 + (int(pad.index)) * joy_max_inputs + int(pad.nbbuttons)
            if input.id == "2":  # SDL_HAT_RIGHT
                hatfirst += 3
            elif input.id == "4":  # SDL_HAT_DOWN
                hatfirst += 1
            elif input.id == "8":  # SDL_HAT_LEFT
                hatfirst += 2
        else:
            hatfirst = (
                1
                + (int(pad.index)) * joy_max_inputs
                + int(pad.nbbuttons)
                + 2 * int(pad.nbaxes)
            )
            if input.id == "2":  # SDL_HAT_RIGHT
                hatfirst += 1
            elif input.id == "4":  # SDL_HAT_DOWN
                hatfirst += 2
            elif input.id == "8":  # SDL_HAT_LEFT
                hatfirst += 3
        value = hatfirst

    elif input.type == "axis":
        axisfirst = (
            1
            + (int(pad.index)) * joy_max_inputs
            + int(pad.nbbuttons)
            + 2 * int(input.id)
        )
        if new_axis_vals:
            axisfirst += int(pad.nbhats) * 4
        if invertAxis:
            axisfirst += 1
        value = axisfirst

    if input.type != "keyboard":
        value += 600

    return value


def setupControllers(config, playersControllers, joy_max_inputs, new_axis_vals):
    # Button control mappings for better readability and maintenance
    CONTROL_MAPPINGS = [
        ("dpup", "MOVEUP"),
        ("dpdown", "MOVEDOWN"),
        ("dpleft", "MOVELEFT"),
        ("dpright", "MOVERIGHT"),
        ("b", "ATTACK"),
        ("x", "ATTACK2"),
        ("leftshoulder", "ATTACK3"),
        ("rightshoulder", "ATTACK4"),
        ("a", "JUMP"),
        ("y", "SPECIAL"),
        ("start", "START"),
        ("triggerleft", "SCREENSHOT"),
        ("guide", "ESC"),
    ]

    # Analog axis mappings (axis_name, inverted, description)
    AXIS_MAPPINGS = [
        ("lefty", False, "axis up"),
        ("lefty", True, "axis down"),
        ("leftx", False, "axis left"),
        ("leftx", True, "axis right"),
    ]

    MAX_PLAYERS = 5
    KEYS_PER_PLAYER = 17  # 0-16

    # Configure controls for each connected player
    for idx, (_, pad) in enumerate(sorted(playersControllers.items())):
        key_idx = 0

        # Configure button controls
        for button, _ in CONTROL_MAPPINGS:
            config.save(
                f"keys.{idx}.{key_idx}",
                JoystickValue(button, pad, joy_max_inputs, new_axis_vals),
            )
            key_idx += 1

        # Configure analog axis controls
        for axis, invert, _ in AXIS_MAPPINGS:
            config.save(
                f"keys.{idx}.{key_idx}",
                JoystickValue(axis, pad, joy_max_inputs, new_axis_vals, invert),
            )
            key_idx += 1

    # Erase old values for unused player slots
    # (prevents a controller from being used in two different positions)
    for idx in range(len(playersControllers), MAX_PLAYERS):
        for key_idx in range(KEYS_PER_PLAYER):
            config.remove(f"keys.{idx}.{key_idx}")
