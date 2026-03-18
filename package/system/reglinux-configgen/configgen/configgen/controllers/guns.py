import os
from pathlib import Path
from re import match
from typing import Any

from evdev.device import InputDevice
from pyudev import Context, Device, Enumerator

from configgen.generators.generator import DeviceConfig
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

        eslog.debug(f"Found mouse {nmouse} at {device_node}")

        if (
            "ID_INPUT_GUN" not in mouse.properties
            or mouse.properties["ID_INPUT_GUN"] != "1"
        ):
            nmouse = nmouse + 1
            continue

        # Try to open the device with proper exception handling
        try:
            if not Path(device_node).exists() or not os.access(device_node, os.R_OK):
                eslog.debug(f"Device {device_node} not accessible")
                nmouse = nmouse + 1
                continue

            device = InputDevice(device_node)
            buttons = getMouseButtons(device)
        except (PermissionError, FileNotFoundError, OSError) as e:
            eslog.debug(f"Device {device_node} access error: {type(e).__name__}")
            nmouse = nmouse + 1
            continue
        except Exception as e:
            eslog.warning(f"Unexpected error with device {device_node}: {e}")
            nmouse = nmouse + 1
            continue

        # retroarch uses mouse indexes into configuration files using ID_INPUT_MOUSE
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
            nmouse = nmouse + 1
            ngun = ngun + 1
        except Exception as e:
            eslog.warning(
                f"Error processing gun properties for device {device_node}: {e}",
            )
            nmouse = nmouse + 1
            continue

    if guns:
        eslog.info(f"Found {len(guns)} gun(s)")
    return guns


def gunsNeedCrosses(guns: DeviceConfig) -> bool:
    """Check if guns need crosshairs.

    Args:
        guns: Gun configuration (dict or list).

    Returns:
        True if crosses are needed.

    """
    # Handle empty guns (no guns = enable crosses for joysticks, mouses...)
    if isinstance(guns, list):
        if len(guns) == 0:
            return True
        # For list format, check if any gun needs a cross
        return any(
            gun.get("need_cross", False) for gun in guns if isinstance(gun, dict)
        )
    # For dict format
    if len(guns) == 0:
        return True
    return any(guns[gun]["need_cross"] for gun in guns)


# returns None is no border is wanted
def guns_borders_size_name(guns: DeviceConfig, config: dict[str, Any]) -> Any:
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

    # Handle both dict and list formats
    if isinstance(guns, list):
        for gun in guns:
            if isinstance(gun, dict) and gun.get("need_borders", False):
                return borders_size
    else:
        for gun in guns:
            if guns[gun].get("need_borders", False):
                return borders_size
    return None
