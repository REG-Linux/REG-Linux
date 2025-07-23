import pyudev
import re
from evdev.device import InputDevice
from .mouse import getMouseButtons

from utils.logger import get_logger
eslog = get_logger(__name__)

def getGuns():

    guns = {}
    context = pyudev.Context()

    # guns are mouses, just filter on them
    mouses = context.list_devices(subsystem='input')

    # keep only mouses with /dev/iput/eventxx
    mouses_clean = {}
    for mouse in mouses:
        matches = re.match(r"^/dev/input/event([0-9]*)$", str(mouse.device_node))
        if matches != None:
            if ("ID_INPUT_MOUSE" in mouse.properties and mouse.properties["ID_INPUT_MOUSE"]) == '1':
                mouses_clean[int(matches.group(1))] = mouse
    mouses = mouses_clean

    nmouse = 0
    ngun   = 0
    for eventid in sorted(mouses):
        eslog.info("found mouse {} at {} with id_mouse={}".format(nmouse, mouses[eventid].device_node, nmouse))
        if "ID_INPUT_GUN" not in mouses[eventid].properties or mouses[eventid].properties["ID_INPUT_GUN"] != "1":
            nmouse = nmouse + 1
            continue

        device = InputDevice(mouses[eventid].device_node)
        buttons = getMouseButtons(device)

        # retroarch uses mouse indexes into configuration files using ID_INPUT_MOUSE (TOUCHPAD are listed after mouses)
        need_cross   = "ID_INPUT_GUN_NEED_CROSS"   in mouses[eventid].properties and mouses[eventid].properties["ID_INPUT_GUN_NEED_CROSS"]   == '1'
        need_borders = "ID_INPUT_GUN_NEED_BORDERS" in mouses[eventid].properties and mouses[eventid].properties["ID_INPUT_GUN_NEED_BORDERS"] == '1'
        guns[ngun] = {"node": mouses[eventid].device_node, "id_mouse": nmouse, "need_cross": need_cross, "need_borders": need_borders, "name": device.name, "buttons": buttons}
        eslog.info("found gun {} at {} with id_mouse={} ({})".format(ngun, mouses[eventid].device_node, nmouse, guns[ngun]["name"]))
        nmouse = nmouse + 1
        ngun = ngun + 1

    if len(guns) == 0:
        eslog.info("no gun found")
    return guns

def gunsNeedCrosses(guns):
    # no gun, enable the cross for joysticks, mouses...
    if len(guns) == 0:
        return True

    for gun in guns:
        if guns[gun]["need_cross"]:
            return True
    return False

# returns None is no border is wanted
def gunsBordersSizeName(guns, config):
    bordersSize = "medium"
    if "controllers.guns.borderssize" in config and config["controllers.guns.borderssize"]:
        bordersSize = config["controllers.guns.borderssize"]

    # overriden by specific options
    bordersmode = "normal"
    if "controllers.guns.bordersmode" in config and config["controllers.guns.bordersmode"] and config["controllers.guns.bordersmode"] != "auto":
        bordersmode = config["controllers.guns.bordersmode"]
    if "bordersmode" in config and config["bordersmode"] and config["bordersmode"] != "auto":
        bordersmode = config["bordersmode"]

    # others are gameonly and normal
    if bordersmode == "hidden":
        return None
    if bordersmode == "force":
        return bordersSize

    for gun in guns:
        if guns[gun]["need_borders"]:
            return bordersSize
    return None

