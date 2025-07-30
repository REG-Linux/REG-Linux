# BigPEmu controller sequence, P1 only requires keyboard inputs
# default standard bindings
P1_BINDINGS_SEQUENCE = {
    "C": {"button": "y", "keyboard": "4"},
    "B": {"button": "b", "keyboard": "22"},
    "A": {"button": "a", "keyboard": "7"},
    "Pause": {"button": "select", "keyboard": "20"},
    "Option": {"button": "start", "keyboard": "26"},
    "Pad-Up": {"button": "up", "keyboard": "82"},
    "Pad-Down": {"button": "down", "keyboard": "81"},
    "Pad-Left": {"button": "left", "keyboard": "80"},
    "Pad-Right": {"button": "right", "keyboard": "79"},
    "Numpad-0": {"buttons": ["r3", "l2"], "keyboard": "39"},
    "Numpad-1": {"buttons": ["y", "l2"], "keyboard": "30"},
    "Numpad-2": {"buttons": ["x", "l2"], "keyboard": "31"},
    "Numpad-3": {"buttons": ["a", "l2"], "keyboard": "32"},
    "Numpad-4": {"button": "pageup", "keyboard": "33"},
    "Numpad-5": {"button": "x", "keyboard": "34"},
    "Numpad-6": {"button": "pagedown", "keyboard": "35"},
    "Numpad-7": {"buttons": ["pageup", "l2"], "keyboard": "36"},
    "Numpad-8": {"buttons": ["b", "l2"], "keyboard": "37"},
    "Numpad-9": {"buttons": ["pagedown", "l2"], "keyboard": "38"},
    "Asterick": {"button": "l3", "keyboard": "18"},
    "Pound": {"button": "r3", "keyboard": "19"},
    "Analog-0-left": {"button": "joystick1left"},
    #"Analog-0-right": {"button": "joystick1right"},
    "Analog-0-up": {"button": "joystick1up"},
    #"Analog-0-down": {"button": "joystick1down"},
    "Analog-1-left": {"button": "joystick2left"},
    #"Analog-1-right": {"button": "joystick2right"},
    "Analog-1-up": {"button": "joystick2up"},
    #"Analog-1-down": {"button": "joystick2down"},
    "Extra-Up": {"blank": None},
    "Extra-Down": {"blank": None},
    "Extra-Left": {"blank": None},
    "Extra-Right": {"blank": None},
    "Extra-A": {"blank": None},
    "Extra-B": {"blank": None},
    "Extra-C": {"blank": None},
    "Extra-D": {"blank": None},
    "Menu": {"buttons": ["start", "r2"], "keyboard": "41"},
    "Fast Forward": {"buttons": ["x", "r2"], "keyboard": "59"},
    "Rewind": {"blank": None},
    "Save State": {"blank": None},
    "Load State": {"blank": None},
    "Screenshot": {"blank": None},
    "Overlay": {"buttons": ["l3", "r2"]},
    "Chat": {"keyboard": "23"},
    "Blank1": {"blank": None},
    "Blank2": {"blank": None},
    "Blank3": {"blank": None},
    "Blank4": {"blank": None},
    "Blank5": {"blank": None}
}

# BigPEmu controller sequence, P2+
# default standard bindings
P2_BINDINGS_SEQUENCE = {
    "C": {"button": "y"},
    "B": {"button": "b"},
    "A": {"button": "a"},
    "Pause": {"button": "select"},
    "Option": {"button": "start"},
    "Pad-Up": {"button": "up"},
    "Pad-Down": {"button": "down"},
    "Pad-Left": {"button": "left"},
    "Pad-Right": {"button": "right"},
    "Numpad-0": {"buttons": ["r3", "l2"]},
    "Numpad-1": {"buttons": ["y", "l2"]},
    "Numpad-2": {"buttons": ["x", "l2"]},
    "Numpad-3": {"buttons": ["a", "l2"]},
    "Numpad-4": {"button": "pageup"},
    "Numpad-5": {"button": "x"},
    "Numpad-6": {"button": "pagedown"},
    "Numpad-7": {"buttons": ["pageup", "l2"]},
    "Numpad-8": {"buttons": ["b", "l2"]},
    "Numpad-9": {"buttons": ["pagedown", "l2"]},
    "Asterick": {"button": "l3"},
    "Pound": {"button": "r3"},
    "Analog-0-left": {"button": "joystick1left"},
    #"Analog-0-right": {"button": "joystick1right"},
    "Analog-0-up": {"button": "joystick1up"},
    #"Analog-0-down": {"button": "joystick1down"},
    "Analog-1-left": {"button": "joystick2left"},
    #"Analog-1-right": {"button": "joystick2right"},
    "Analog-1-up": {"button": "joystick2up"},
    #"Analog-1-down": {"button": "joystick2down"},
    "Extra-Up": {"blank": None},
    "Extra-Down": {"blank": None},
    "Extra-Left": {"blank": None},
    "Extra-Right": {"blank": None},
    "Extra-A": {"blank": None},
    "Extra-B": {"blank": None},
    "Extra-C": {"blank": None},
    "Extra-D": {"blank": None}
}

def generate_keyb_button_bindings(device_id, keyb_id, button_id, button_value):
    device_id = device_id.upper()
    bindings = []
    binding = {
        "Triggers": [
            {
                "B_KB": True,
                "B_ID": int(keyb_id),
                "B_AH": 0.0
            },
            {
                "B_KB": False,
                "B_ID": int(button_id),
                "B_AH": float(button_value),
                "B_DevID": device_id
            }
        ]
    }
    bindings.append(binding)
    return bindings

def generate_button_bindings(device_id, button_id, button_value):
    device_id = device_id.upper()
    bindings = []
    binding = {
        "Triggers": [
            {
                "B_KB": False,
                "B_ID": int(button_id),
                "B_AH": float(button_value),
                "B_DevID": device_id
            }
        ]
    }
    bindings.append(binding)
    return bindings

def generate_keyb_combo_bindings(device_id, keyb_id, button_id, button_value, analog_id, analog_value):
    device_id = device_id.upper()
    bindings = []
    binding = {
        "Triggers": [
            {
                "B_KB": True,
                "B_ID": int(keyb_id),
                "B_AH": 0.0
            },
            {
                "B_KB": False,
                "B_ID": int(button_id),
                "B_AH": float(button_value),
                "B_DevID": device_id,
                "M_KB": False,
                "M_ID": int(analog_id),
                "M_AH": float(analog_value),
                "M_DevID": device_id
            }
        ]
    }
    bindings.append(binding)
    return bindings

def generate_combo_bindings(device_id, button_id, button_value, analog_id, analog_value):
    device_id = device_id.upper()
    bindings = []
    binding = {
        "Triggers": [
            {
                "B_KB": False,
                "B_ID": int(button_id),
                "B_AH": float(button_value),
                "B_DevID": device_id,
                "M_KB": False,
                "M_ID": int(analog_id),
                "M_AH": float(analog_value),
                "M_DevID": device_id
            }
        ]
    }
    bindings.append(binding)
    return bindings

def generate_blank_bindings():
    bindings = []
    binding = {
        "Triggers": []
    }
    bindings.append(binding)
    return bindings

def generate_keyb_bindings(keyb_id):
    bindings = []
    binding = {
        "Triggers": [
            {
                "B_KB": True,
                "B_ID": int(keyb_id),
                "B_AH": 0.0
            }
        ]
    }
    bindings.append(binding)
    return bindings
