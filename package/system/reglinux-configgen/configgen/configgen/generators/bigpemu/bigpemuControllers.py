# BigPEmu controller sequence, P1 only requires keyboard inputs
# default standard bindings
P1_BINDINGS_SEQUENCE = {
    "C": {"button": "y", "keyboard": "4"},
    "B": {"button": "b", "keyboard": "22"},
    "A": {"button": "a", "keyboard": "7"},
    "Pause": {"button": "back", "keyboard": "20"},
    "Option": {"button": "start", "keyboard": "26"},
    "Pad-Up": {"button": "dpup", "keyboard": "82"},
    "Pad-Down": {"button": "dpdown", "keyboard": "81"},
    "Pad-Left": {"button": "dpleft", "keyboard": "80"},
    "Pad-Right": {"button": "dpright", "keyboard": "79"},
    "Numpad-0": {"buttons": ["rightstick", "triggerleft"], "keyboard": "39"},
    "Numpad-1": {"buttons": ["y", "triggerleft"], "keyboard": "30"},
    "Numpad-2": {"buttons": ["x", "triggerleft"], "keyboard": "31"},
    "Numpad-3": {"buttons": ["a", "triggerleft"], "keyboard": "32"},
    "Numpad-4": {"button": "leftshoulder", "keyboard": "33"},
    "Numpad-5": {"button": "x", "keyboard": "34"},
    "Numpad-6": {"button": "rightshoulder", "keyboard": "35"},
    "Numpad-7": {"buttons": ["leftshoulder", "triggerleft"], "keyboard": "36"},
    "Numpad-8": {"buttons": ["b", "triggerleft"], "keyboard": "37"},
    "Numpad-9": {"buttons": ["rightshoulder", "triggerleft"], "keyboard": "38"},
    "Asterick": {"button": "leftstick", "keyboard": "18"},
    "Pound": {"button": "rightstick", "keyboard": "19"},
    "Analog-0-left": {"button": "joystick1left"},
    #"Analog-0-right": {"button": "joystick1right"},
    "Analog-0-up": {"button": "lefty"},
    #"Analog-0-down": {"button": "joystick1down"},
    "Analog-1-left": {"button": "rightx"},
    #"Analog-1-right": {"button": "joystick2right"},
    "Analog-1-up": {"button": "righty"},
    #"Analog-1-down": {"button": "joystick2down"},
    "Extra-Up": {"blank": None},
    "Extra-Down": {"blank": None},
    "Extra-Left": {"blank": None},
    "Extra-Right": {"blank": None},
    "Extra-A": {"blank": None},
    "Extra-B": {"blank": None},
    "Extra-C": {"blank": None},
    "Extra-D": {"blank": None},
    "Menu": {"buttons": ["start", "triggerright"], "keyboard": "41"},
    "Fast Forward": {"buttons": ["x", "triggerright"], "keyboard": "59"},
    "Rewind": {"blank": None},
    "Save State": {"blank": None},
    "Load State": {"blank": None},
    "Screenshot": {"blank": None},
    "Overlay": {"buttons": ["leftstick", "triggerright"]},
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
    "Pad-Up": {"button": "dpup"},
    "Pad-Down": {"button": "dpdown"},
    "Pad-Left": {"button": "dpleft"},
    "Pad-Right": {"button": "dpright"},
    "Numpad-0": {"buttons": ["rightstick", "triggerleft"]},
    "Numpad-1": {"buttons": ["y", "triggerleft"]},
    "Numpad-2": {"buttons": ["x", "triggerleft"]},
    "Numpad-3": {"buttons": ["a", "triggerleft"]},
    "Numpad-4": {"button": "leftshoulder"},
    "Numpad-5": {"button": "x"},
    "Numpad-6": {"button": "rightshoulder"},
    "Numpad-7": {"buttons": ["leftshoulder", "triggerleft"]},
    "Numpad-8": {"buttons": ["b", "triggerleft"]},
    "Numpad-9": {"buttons": ["rightshoulder", "triggerleft"]},
    "Asterick": {"button": "leftstick"},
    "Pound": {"button": "rightstick"},
    "Analog-0-left": {"button": "joystick1left"},
    #"Analog-0-right": {"button": "joystick1right"},
    "Analog-0-up": {"button": "lefty"},
    #"Analog-0-down": {"button": "joystick1down"},
    "Analog-1-left": {"button": "rightx"},
    #"Analog-1-right": {"button": "joystick2right"},
    "Analog-1-up": {"button": "righty"},
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

def setBigPEmuControllers(bigpemuConfig, playersControllers):
    # Controller config
    if "Input" not in bigpemuConfig["BigPEmuConfig"]:
        bigpemuConfig["BigPEmuConfig"]["Input"] = {}

        # initial settings
        bigpemuConfig["BigPEmuConfig"]["Input"]["DeviceCount"] = len(playersControllers)
        bigpemuConfig["BigPEmuConfig"]["Input"]["AnalDeadMice"] = 0.25
        bigpemuConfig["BigPEmuConfig"]["Input"]["AnalToDigi"] = 0.25
        bigpemuConfig["BigPEmuConfig"]["Input"]["AnalExpo"] = 0.0
        bigpemuConfig["BigPEmuConfig"]["Input"]["ConflictingPad"] = 0
        bigpemuConfig["BigPEmuConfig"]["Input"]["XboxAnus"] = 0
        bigpemuConfig["BigPEmuConfig"]["Input"]["OLAnchor"] = 3
        bigpemuConfig["BigPEmuConfig"]["Input"]["OLScale"] = 0.75
        bigpemuConfig["BigPEmuConfig"]["Input"]["MouseInput"] = 0
        bigpemuConfig["BigPEmuConfig"]["Input"]["MouseSens"] = 1.0
        bigpemuConfig["BigPEmuConfig"]["Input"]["MouseThresh"] = 0.5
