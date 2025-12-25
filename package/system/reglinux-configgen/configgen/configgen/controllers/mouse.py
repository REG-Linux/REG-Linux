from typing import Any, List, Optional

from evdev import ecodes


def getMouseButtons(device: Any) -> List[str]:
    caps = device.capabilities()
    caps_keys = caps[ecodes.EV_KEY]
    caps_filter = [
        ecodes.BTN_LEFT,
        ecodes.BTN_RIGHT,
        ecodes.BTN_MIDDLE,
        ecodes.BTN_1,
        ecodes.BTN_2,
        ecodes.BTN_3,
        ecodes.BTN_4,
        ecodes.BTN_5,
        ecodes.BTN_6,
        ecodes.BTN_7,
        ecodes.BTN_8,
    ]
    caps_intersection = list(set(caps_keys) & set(caps_filter))
    buttons = []
    if ecodes.BTN_LEFT in caps_intersection:
        buttons.append("left")
    if ecodes.BTN_RIGHT in caps_intersection:
        buttons.append("right")
    if ecodes.BTN_MIDDLE in caps_intersection:
        buttons.append("middle")
    if ecodes.BTN_1 in caps_intersection:
        buttons.append("1")
    if ecodes.BTN_2 in caps_intersection:
        buttons.append("2")
    if ecodes.BTN_3 in caps_intersection:
        buttons.append("3")
    if ecodes.BTN_4 in caps_intersection:
        buttons.append("4")
    if ecodes.BTN_5 in caps_intersection:
        buttons.append("5")
    if ecodes.BTN_6 in caps_intersection:
        buttons.append("6")
    if ecodes.BTN_7 in caps_intersection:
        buttons.append("7")
    if ecodes.BTN_8 in caps_intersection:
        buttons.append("8")
    return buttons


def mouseButtonToCode(button: str) -> Optional[int]:
    if button == "left":
        return ecodes.BTN_LEFT
    if button == "right":
        return ecodes.BTN_RIGHT
    if button == "middle":
        return ecodes.BTN_MIDDLE
    if button == "1":
        return ecodes.BTN_1
    if button == "2":
        return ecodes.BTN_2
    if button == "3":
        return ecodes.BTN_3
    if button == "4":
        return ecodes.BTN_4
    if button == "5":
        return ecodes.BTN_5
    if button == "6":
        return ecodes.BTN_6
    if button == "7":
        return ecodes.BTN_7
    if button == "8":
        return ecodes.BTN_8
    return None
