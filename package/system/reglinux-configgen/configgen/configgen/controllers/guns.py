import os
from pathlib import Path
from re import match
from typing import Any

from evdev.device import InputDevice
from pyudev import Context, Device, Enumerator

from configgen.utils.logger import get_logger

from .mouse import getMouseButtons

eslog = get_logger(__name__)


def getGuns() -> dict[str, Any]:
    guns: dict[str, Any] = {}
    try:
        context = Context()
    except Exception as e:
        eslog.error(f"Failed to initialize pyudev context: {e}")
        return guns

    # guns are mouses, just filter on them
    try:
        mouses: Enumerator = context.list_devices(subsystem="input")
    except Exception as e:
        eslog.error(f"Failed to list input devices: {e}")
        return guns

    # keep only mouses with /dev/input/eventxx
    mouses_clean: dict[int, Device] = {}
    mouses_list = list(mouses)
    for mouse in mouses_list:
        mouse: Device
        try:
            device_node = (
                str(mouse.device_node) if mouse.device_node is not None else ""
            )
            matches = match(r"^/dev/input/event([0-9]*)$", device_node)
            if (
                matches is not None
                and (
                    "ID_INPUT_MOUSE" in mouse.properties
                    and mouse.properties["ID_INPUT_MOUSE"]
                )
                == "1"
            ):
                mouses_clean[int(matches.group(1))] = mouse
        except (AttributeError, ValueError) as e:
            eslog.warning(
                f"Error processing mouse device {mouse.device_node if hasattr(mouse, 'device_node') else 'unknown'}: {e}",
            )
            continue
        except Exception as e:
            eslog.warning(
                f"Unexpected error processing mouse device {mouse.device_node if hasattr(mouse, 'device_node') else 'unknown'}: {e}",
            )
            continue

    mouses_dict: dict[int, Device] = mouses_clean

    nmouse = 0
    ngun = 0
    for eventid in sorted(mouses_dict):
        mouse: Device = mouses_dict[eventid]
        device_node = str(mouse.device_node) if mouse.device_node is not None else ""

        eslog.info(f"found mouse {nmouse} at {device_node} with id_mouse={nmouse}")

        if (
            "ID_INPUT_GUN" not in mouse.properties
            or mouse.properties["ID_INPUT_GUN"] != "1"
        ):
            nmouse = nmouse + 1
            continue

        # Try to open the device with proper exception handling
        try:
            if not Path(device_node).exists() or not os.access(device_node, os.R_OK):
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
            need_cross: bool = (
                "ID_INPUT_GUN_NEED_CROSS" in mouse.properties
                and mouse.properties["ID_INPUT_GUN_NEED_CROSS"] == "1"
            )
            need_borders: bool = (
                "ID_INPUT_GUN_NEED_BORDERS" in mouse.properties
                and mouse.properties["ID_INPUT_GUN_NEED_BORDERS"] == "1"
            )
            guns[str(ngun)] = {
                "node": device_node,
                "id_mouse": nmouse,
                "need_cross": need_cross,
                "need_borders": need_borders,
                "name": device.name,
                "buttons": buttons,
            }
            eslog.info(
                f"found gun {ngun} at {device_node} with id_mouse={nmouse} ({guns[str(ngun)]['name']})",
            )
            nmouse = nmouse + 1
            ngun = ngun + 1
        except Exception as e:
            eslog.warning(
                f"Error processing gun properties for device {device_node}: {e}",
            )
            nmouse = nmouse + 1
            continue

    if len(guns) == 0:
        eslog.info("no gun found")
    return guns


def gunsNeedCrosses(guns: dict[str, Any]) -> bool:
    # no gun, enable the cross for joysticks, mouses...
    if len(guns) == 0:
        return True

    return any(guns[gun]["need_cross"] for gun in guns)


# returns None is no border is wanted
def guns_borders_size_name(guns: dict[str, Any], config: dict[str, Any]) -> Any:
    borders_size: str = "medium"
    if config.get("controllers.guns.borderssize"):
        borders_size = config["controllers.guns.borderssize"]

    # overriden by specific options
    borders_mode: str = "normal"
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
