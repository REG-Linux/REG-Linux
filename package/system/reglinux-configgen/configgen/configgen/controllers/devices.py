from typing import Any, Dict, List, Optional

from pyudev import Context

from .utils import dev2int


def getDevicesInformation() -> Dict[str, Any]:
    groups: Dict[str, Any] = {}
    devices: Dict[str, Any] = {}
    context = Context()
    events = context.list_devices(subsystem="input")
    mouses: List[int] = []
    joysticks: List[int] = []
    for ev in events:
        eventId = dev2int(str(ev.device_node))
        if eventId is not None:
            isJoystick: bool = (
                "ID_INPUT_JOYSTICK" in ev.properties
                and ev.properties["ID_INPUT_JOYSTICK"] == "1"
            )
            isWheel: bool = (
                "ID_INPUT_WHEEL" in ev.properties
                and ev.properties["ID_INPUT_WHEEL"] == "1"
            )
            isMouse: bool = (
                "ID_INPUT_MOUSE" in ev.properties
                and ev.properties["ID_INPUT_MOUSE"] == "1"
            ) or (
                "ID_INPUT_TOUCHPAD" in ev.properties
                and ev.properties["ID_INPUT_TOUCHPAD"] == "1"
            )
            group: Optional[str] = None
            if "ID_PATH" in ev.properties:
                group = ev.properties["ID_PATH"]
            if isJoystick or isMouse:
                if isJoystick:
                    joysticks.append(eventId)
                if isMouse:
                    mouses.append(eventId)
                devices[str(eventId)] = {
                    "node": ev.device_node,
                    "group": group,
                    "isJoystick": isJoystick,
                    "isWheel": isWheel,
                    "isMouse": isMouse,
                }
                if "ID_PATH" in ev.properties and group is not None:
                    if isWheel and "WHEEL_ROTATION_ANGLE" in ev.properties:
                        devices[str(eventId)]["wheel_rotation"] = int(
                            ev.properties["WHEEL_ROTATION_ANGLE"]
                        )
                    if group not in groups:
                        groups[group] = []
                    groups[group].append(ev.device_node)
    mouses.sort()
    joysticks.sort()
    res: Dict[str, Any] = {}
    for device in devices:
        d = devices[device]
        dgroup: Optional[List[str]] = None
        if d["group"] is not None and d["group"] in groups:
            dgroup = groups[d["group"]].copy()
            if dgroup is not None and d["node"] in dgroup:
                dgroup.remove(d["node"])
        nmouse: Optional[int] = None
        njoystick: Optional[int] = None
        if d["isJoystick"]:
            try:
                njoystick = joysticks.index(int(device))
            except (ValueError, TypeError):
                njoystick = None
        if d["isMouse"]:
            try:
                nmouse = mouses.index(int(device))
            except (ValueError, TypeError):
                nmouse = None
        res[d["node"]] = {
            "eventId": device,
            "isJoystick": d["isJoystick"],
            "isWheel": d["isWheel"],
            "isMouse": d["isMouse"],
            "associatedDevices": dgroup,
            "joystick_index": njoystick,
            "mouse_index": nmouse,
        }
        if "wheel_rotation" in d:
            res[d["node"]]["wheel_rotation"] = d["wheel_rotation"]
    return res


def getAssociatedMouse(
    devicesInformation: Dict[str, Any], dev: str
) -> Optional[Dict[str, Any]]:
    if (
        dev not in devicesInformation
        or devicesInformation[dev]["associatedDevices"] is None
    ):
        return None
    for candidate in devicesInformation[dev]["associatedDevices"]:
        if devicesInformation[candidate]["isMouse"]:
            return candidate
    return None
