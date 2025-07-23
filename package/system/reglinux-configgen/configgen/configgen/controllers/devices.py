import pyudev
from .utils import dev2int

def getDevicesInformation():
  groups    = {}
  devices   = {}
  context   = pyudev.Context()
  events    = context.list_devices(subsystem='input')
  mouses    = []
  joysticks = []
  for ev in events:
    eventId = dev2int(str(ev.device_node))
    if eventId != None:
      isJoystick = ("ID_INPUT_JOYSTICK" in ev.properties and ev.properties["ID_INPUT_JOYSTICK"] == "1")
      isWheel    = ("ID_INPUT_WHEEL"    in ev.properties and ev.properties["ID_INPUT_WHEEL"] == "1")
      isMouse    = ("ID_INPUT_MOUSE"    in ev.properties and ev.properties["ID_INPUT_MOUSE"] == "1") or ("ID_INPUT_TOUCHPAD" in ev.properties and ev.properties["ID_INPUT_TOUCHPAD"] == "1")
      group = None
      if "ID_PATH" in ev.properties:
        group = ev.properties["ID_PATH"]
      if isJoystick or isMouse:
        if isJoystick:
          joysticks.append(eventId)
        if isMouse:
          mouses.append(eventId)
        devices[eventId] = { "node": ev.device_node, "group": group, "isJoystick": isJoystick, "isWheel": isWheel, "isMouse": isMouse }
        if "ID_PATH" in ev.properties:
          if isWheel and "WHEEL_ROTATION_ANGLE" in ev.properties:
              devices[eventId]["wheel_rotation"] = int(ev.properties["WHEEL_ROTATION_ANGLE"])
          if group not in groups:
            groups[group] = []
          groups[group].append(ev.device_node)
  mouses.sort()
  joysticks.sort()
  res = {}
  for device in devices:
    d = devices[device]
    dgroup = None
    if d["group"] is not None:
        dgroup = groups[d["group"]].copy()
        dgroup.remove(d["node"])
    nmouse    = None
    njoystick = None
    if d["isJoystick"]:
      njoystick = joysticks.index(device)
    nmouse = None
    if d["isMouse"]:
      nmouse = mouses.index(device)
    res[d["node"]] = { "eventId": device, "isJoystick": d["isJoystick"], "isWheel": d["isWheel"], "isMouse": d["isMouse"], "associatedDevices": dgroup, "joystick_index": njoystick, "mouse_index": nmouse }
    if "wheel_rotation" in d:
        res[d["node"]]["wheel_rotation"] = d["wheel_rotation"]
  return res

def getAssociatedMouse(devicesInformation, dev):
    if dev not in devicesInformation or devicesInformation[dev]["associatedDevices"] is None:
        return None
    for candidate in devicesInformation[dev]["associatedDevices"]:
        if devicesInformation[candidate]["isMouse"]:
            return candidate
    return None
