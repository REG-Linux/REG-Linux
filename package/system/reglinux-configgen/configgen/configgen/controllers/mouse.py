import evdev

def getMouseButtons(device):
  caps = device.capabilities()
  caps_keys = caps[evdev.ecodes.EV_KEY]
  caps_filter = [evdev.ecodes.BTN_LEFT, evdev.ecodes.BTN_RIGHT, evdev.ecodes.BTN_MIDDLE, evdev.ecodes.BTN_1, evdev.ecodes.BTN_2, evdev.ecodes.BTN_3, evdev.ecodes.BTN_4, evdev.ecodes.BTN_5, evdev.ecodes.BTN_6, evdev.ecodes.BTN_7, evdev.ecodes.BTN_8]
  caps_intersection = list(set(caps_keys) & set(caps_filter))
  buttons = []
  if evdev.ecodes.BTN_LEFT in caps_intersection:
    buttons.append("left")
  if evdev.ecodes.BTN_RIGHT in caps_intersection:
    buttons.append("right")
  if evdev.ecodes.BTN_MIDDLE in caps_intersection:
    buttons.append("middle")
  if evdev.ecodes.BTN_1 in caps_intersection:
    buttons.append("1")
  if evdev.ecodes.BTN_2 in caps_intersection:
    buttons.append("2")
  if evdev.ecodes.BTN_3 in caps_intersection:
    buttons.append("3")
  if evdev.ecodes.BTN_4 in caps_intersection:
    buttons.append("4")
  if evdev.ecodes.BTN_5 in caps_intersection:
    buttons.append("5")
  if evdev.ecodes.BTN_6 in caps_intersection:
    buttons.append("6")
  if evdev.ecodes.BTN_7 in caps_intersection:
    buttons.append("7")
  if evdev.ecodes.BTN_8 in caps_intersection:
    buttons.append("8")
  return buttons

def mouseButtonToCode(button):
    if button == "left":
        return evdev.ecodes.BTN_LEFT
    if button == "right":
        return evdev.ecodes.BTN_RIGHT
    if button == "middle":
        return evdev.ecodes.BTN_MIDDLE
    if button == "1":
        return evdev.ecodes.BTN_1
    if button == "2":
        return evdev.ecodes.BTN_2
    if button == "3":
        return evdev.ecodes.BTN_3
    if button == "4":
        return evdev.ecodes.BTN_4
    if button == "5":
        return evdev.ecodes.BTN_5
    if button == "6":
        return evdev.ecodes.BTN_6
    if button == "7":
        return evdev.ecodes.BTN_7
    if button == "8":
        return evdev.ecodes.BTN_8
    return None

