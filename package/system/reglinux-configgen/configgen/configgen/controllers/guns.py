import os
from os import path
from re import match
from typing import Any, Dict, List

from evdev.device import InputDevice
from pyudev import Context

from configgen.utils.logger import get_logger

from .mouse import getMouseButtons

eslog = get_logger(__name__)


def getGuns() -> Dict[str, Any]:
    guns = {}
    try:
        context = Context()
    except Exception as e:
        eslog.error(f"Failed to initialize pyudev context: {e}")
        return guns

    # guns are mouses, just filter on them
    try:
        mouses = context.list_devices(subsystem="input")
    except Exception as e:
        eslog.error(f"Failed to list input devices: {e}")
        return guns

    # keep only mouses with /dev/input/eventxx
    mouses_clean = {}
    for mouse in mouses:
        try:
            device_node = str(mouse.device_node)
            matches = match(r"^/dev/input/event([0-9]*)$", device_node)
            if matches is not None:
                if (
                    "ID_INPUT_MOUSE" in mouse.properties
                    and mouse.properties["ID_INPUT_MOUSE"]
                ) == "1":
                    mouses_clean[int(matches.group(1))] = mouse
        except (AttributeError, ValueError) as e:
            eslog.warning(
                f"Error processing mouse device {mouse.device_node if hasattr(mouse, 'device_node') else 'unknown'}: {e}"
            )
            continue
        except Exception as e:
            eslog.warning(
                f"Unexpected error processing mouse device {mouse.device_node if hasattr(mouse, 'device_node') else 'unknown'}: {e}"
            )
            continue

    mouses = mouses_clean

    nmouse = 0
    ngun = 0
    for eventid in sorted(mouses):
        mouse = mouses[eventid]
        device_node = str(mouse.device_node)

        eslog.info(f"found mouse {nmouse} at {device_node} with id_mouse={nmouse}")

        if (
            "ID_INPUT_GUN" not in mouse.properties
            or mouse.properties["ID_INPUT_GUN"] != "1"
        ):
            nmouse = nmouse + 1
            continue

        # Try to open the device with proper exception handling
        try:
            if not path.exists(device_node) or not os.access(device_node, os.R_OK):
                eslog.warning(f"Device {device_node} does not exist or is not readable")
                nmouse = nmouse + 1
                continue

            device = InputDevice(device_node)
            buttons = getMouseButtons(device)
        except PermissionError as e:
            eslog.warning(f"Permission denied accessing device {device_node}: {e}")
            nmouse = nmouse + 1
            continue
        except FileNotFoundError as e:
            eslog.warning(f"Device not found at {device_node}: {e}")
            nmouse = nmouse + 1
            continue
        except OSError as e:
            eslog.warning(f"OS error accessing device {device_node}: {e}")
            nmouse = nmouse + 1
            continue
        except Exception as e:
            eslog.warning(f"Error opening device {device_node}: {e}")
            nmouse = nmouse + 1
            continue

        # retroarch uses mouse indexes into configuration files using ID_INPUT_MOUSE (TOUCHPAD are listed after mouses)
        try:
            need_cross = (
                "ID_INPUT_GUN_NEED_CROSS" in mouse.properties
                and mouse.properties["ID_INPUT_GUN_NEED_CROSS"] == "1"
            )
            need_borders = (
                "ID_INPUT_GUN_NEED_BORDERS" in mouse.properties
                and mouse.properties["ID_INPUT_GUN_NEED_BORDERS"] == "1"
            )
            guns[ngun] = {
                "node": device_node,
                "id_mouse": nmouse,
                "need_cross": need_cross,
                "need_borders": need_borders,
                "name": device.name,
                "buttons": buttons,
            }
            eslog.info(
                "found gun {} at {} with id_mouse={} ({})".format(
                    ngun, device_node, nmouse, guns[ngun]["name"]
                )
            )
            nmouse = nmouse + 1
            ngun = ngun + 1
        except Exception as e:
            eslog.warning(
                f"Error processing gun properties for device {device_node}: {e}"
            )
            nmouse = nmouse + 1
            continue

    if len(guns) == 0:
        eslog.info("no gun found")
    return guns


def gunsNeedCrosses(guns: List[Any]) -> bool:
    # no gun, enable the cross for joysticks, mouses...
    if len(guns) == 0:
        return True

    for gun in guns:
        if guns[gun]["need_cross"]:
            return True
    return False


# returns None is no border is wanted
def guns_borders_size_name(guns: List[Any], config: Dict[str, Any]) -> Any:
    borders_size = "medium"
    if (
        "controllers.guns.borderssize" in config
        and config["controllers.guns.borderssize"]
    ):
        borders_size = config["controllers.guns.borderssize"]

    # overriden by specific options
    borders_mode = "normal"
    if (
        "controllers.guns.bordersmode" in config
        and config["controllers.guns.bordersmode"]
        and config["controllers.guns.bordersmode"] != "auto"
    ):
        borders_mode = config["controllers.guns.bordersmode"]
    if (
        "bordersmode" in config
        and config["bordersmode"]
        and config["bordersmode"] != "auto"
    ):
        borders_mode = config["bordersmode"]

    # others are gameonly and normal
    if borders_mode == "hidden":
        return None
    if borders_mode == "force":
        return borders_size

    for gun in guns:
        if guns[gun]["need_borders"]:
            return borders_size
    return None
