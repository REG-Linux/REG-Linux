from typing import Any


def setMelondsControllers(melondsConfig: Any, playersControllers: Any) -> None:
    """Configure melonDS controller mappings.

    melonDS uses direct SDL button/axis indices:
    - Buttons use their SDL index directly (0, 1, 2, 3...)
    - D-Pad uses special SDL workaround values (257, 260, 264, 258)
    """
    # Map controllers - supports both 'dpup' and 'up' naming conventions
    melonDSMapping = {
        "a": "A",
        "b": "B",
        "back": "Select",
        "start": "Start",
        # D-Pad (hat) - names vary by controller
        "right": "Right",
        "dpright": "Right",
        "left": "Left",
        "dpleft": "Left",
        "up": "Up",
        "dpup": "Up",
        "down": "Down",
        "dpdown": "Down",
        "rightshoulder": "R",
        "leftshoulder": "L",
        "x": "X",
        "y": "Y",
    }

    # Initialize Instance0.Joystick section if it doesn't exist
    if "Instance0" not in melondsConfig:
        melondsConfig["Instance0"] = {}
    if "Joystick" not in melondsConfig["Instance0"]:
        melondsConfig["Instance0"]["Joystick"] = {}

    joystick = melondsConfig["Instance0"]["Joystick"]

    for _, pad in sorted(playersControllers.items()):
        # Only use Player 1 controls (index 0)
        # Handle both string and int index types
        if str(pad.index) != "0":
            continue

        for index in pad.inputs:
            input_obj = pad.inputs[index]
            if input_obj.name not in melonDSMapping:
                continue

            option = melonDSMapping[input_obj.name]

            # Get the SDL input ID (e.g., "0", "1", "2" for buttons)
            val = input_obj.id

            # Workaround - SDL numbers for D-Pad
            # For hat inputs (h0.1, h0.2, h0.4, h0.8), use special values
            # For button inputs with id "0", also use special values
            if option in ["Up", "Down", "Left", "Right"]:
                if input_obj.type == "hat":
                    # Hat id format: h0.1 (up), h0.2 (right), h0.4 (down), h0.8 (left)
                    # Use input_obj.id which contains the hat format (e.g., "h0.1")
                    hat_id = input_obj.id
                    if "." in hat_id:
                        # Map hat direction to melonDS special values
                        if option == "Up":
                            val = 257
                        elif option == "Down":
                            val = 260
                        elif option == "Left":
                            val = 264
                        elif option == "Right":
                            val = 258
                elif val == "0":
                    # Button-based D-Pad with id "0"
                    if option == "Up":
                        val = 257
                    elif option == "Down":
                        val = 260
                    elif option == "Left":
                        val = 264
                    elif option == "Right":
                        val = 258

            joystick[option] = int(val)

    # Always set ID to 0
    joystick["JoystickID"] = 0
