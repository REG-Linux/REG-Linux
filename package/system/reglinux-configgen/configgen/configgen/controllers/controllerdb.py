"""
Controller database management.
Handles loading and matching controller configurations from gamecontrollerdb.txt.
"""

from os import environ
from typing import Dict, List, Type
from controllers import Controller, Input
from concurrent.futures import ThreadPoolExecutor
from utils.logger import get_logger

eslog = get_logger(__name__)

@staticmethod
def parse_line(line: str) -> tuple[str, dict] | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    parts = line.split(",")
    if len(parts) < 2:
        return None
    guid = parts[0]
    name = parts[1]
    inputs = {}
    for input_pair in parts[2:]:
        input_pair = input_pair.strip()
        if ":" not in input_pair:
            continue
        key, value = input_pair.split(":", 1)
        key = key.strip()
        value = value.strip()
        # Create Input object for each mapping
        input_obj = Input.from_sdl_mapping(key, value)
        if input_obj:
            inputs[key] = input_obj
    return guid, {
        "guid": guid,
        "name": name,
        "inputs": inputs,
        "type": "joystick",
        "input_objects": inputs,  # Backward compatible
    }


def load_all_controllers_config() -> Dict[str, Dict]:
    """
    Load all controller configurations from gamecontrollerdb.txt.
    Enhanced version that creates Input objects for each controller input.

    Returns:
        Dictionary mapping GUIDs to controller configurations with Input objects
    """
    controllerdb = {}
    filepath = environ.get("SDL_GAMECONTROLLERCONFIG_FILE", "gamecontrollerdb.txt")

    try:
        with open(filepath, "r") as f:
            lines = f.readlines()

        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda line: parse_line(line), lines)

        for res in results:
            if res is not None:
                guid, config = res
                controllerdb[guid] = config

    except FileNotFoundError:
        eslog.warning(f"Warning: Controller config file {filepath} not found.")
    except Exception as e:
        eslog.error(f"Error loading controller config: {e}")

    return controllerdb

def load_controller_config(controllersInput):
    """
    Generates player-specific controller objects using the known controller database.

    Args:
        controllersInput (list): List of controller input descriptors containing "guid" and "devicepath".

    Returns:
        dict: Dictionary of Controller instances keyed by player number (as strings).
    """
    playerControllers = dict()
    controllers = load_all_controllers_config()

    for i, ci in enumerate(controllersInput):
        newController = _find_best_controller_config(
            controllers, i, ci["guid"], ci["devicepath"]
        )
        if newController:
            playerControllers[str(i + 1)] = newController
    return playerControllers


def _find_best_controller_config(controllers, x, pxguid, pxdev):
    """
    Finds the best controller match in the loaded database by GUID and returns a Controller instance.

    Args:
        controllers (dict): Dictionary of available controller configurations.
        x (str): Player index (as string).
        pxguid (str): GUID of the connected controller.
        pxdev (str): Device path of the connected controller.

    Returns:
        Controller | None: Matched Controller instance or None if not found.
    """
    for controllerGUID in controllers:
        controller = controllers[controllerGUID]
        if controller["guid"] == pxguid:
            controller_data = controller.copy()
            controller_data["index"] = x
            controller_data["dev"] = pxdev
            return Controller.from_dict(controller_data)
    return None
