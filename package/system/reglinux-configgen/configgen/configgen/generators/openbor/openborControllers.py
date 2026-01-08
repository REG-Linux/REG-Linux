from typing import Any


def setControllerConfig(config: Any, playersControllers: Any, core: str) -> None:
    if core == "openbor4432":
        setupControllers(config, playersControllers, 32, False)
    elif core == "openbor7142":
        setupControllers(config, playersControllers, 64, True)
    else:
        setupControllers(config, playersControllers, 64, False)


def JoystickValue(
    key: str,
    pad: Any,
    joy_max_inputs: Any,
    new_axis_vals: Any,
    invertAxis: bool = False,
) -> Any:
    if key not in pad.inputs:
        return 0

    value = 0
    input_obj = pad.inputs[key]

    if input_obj.type == "button":
        value = 1 + (int(pad.index)) * joy_max_inputs + int(input_obj.id)

    elif input_obj.type == "hat":
        input_obj.id = input_obj.id[-1]
        if new_axis_vals:
            hatfirst = 1 + (int(pad.index)) * joy_max_inputs + int(pad.nbbuttons)
            if input_obj.id == "2":  # SDL_HAT_RIGHT
                hatfirst += 3
            elif input_obj.id == "4":  # SDL_HAT_DOWN
                hatfirst += 1
            elif input_obj.id == "8":  # SDL_HAT_LEFT
                hatfirst += 2
        else:
            hatfirst = (
                1
                + (int(pad.index)) * joy_max_inputs
                + int(pad.nbbuttons)
                + 2 * int(pad.nbaxes)
            )
            if input_obj.id == "2":  # SDL_HAT_RIGHT
                hatfirst += 1
            elif input_obj.id == "4":  # SDL_HAT_DOWN
                hatfirst += 2
            elif input_obj.id == "8":  # SDL_HAT_LEFT
                hatfirst += 3
        value = hatfirst

    elif input_obj.type == "axis":
        axisfirst = (
            1
            + (int(pad.index)) * joy_max_inputs
            + int(pad.nbbuttons)
            + 2 * int(input_obj.id)
        )
        if new_axis_vals:
            axisfirst += int(pad.nbhats) * 4
        if invertAxis:
            axisfirst += 1
        value = axisfirst

    if input_obj.type != "keyboard":
        value += 600

    return value


def setupControllers(
    config: Any,
    playersControllers: Any,
    joy_max_inputs: Any,
    new_axis_vals: Any,
) -> None:
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
