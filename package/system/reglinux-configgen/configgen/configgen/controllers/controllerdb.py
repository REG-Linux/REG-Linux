"""
Controller database management.
Handles loading and matching controller configurations from gamecontrollerdb.txt.
"""

from os import environ
from typing import Dict
from controllers import Controller, Input

from utils.logger import get_logger
eslog = get_logger(__name__)

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
        with open(filepath, "r") as controllerdb_file:
            for line in controllerdb_file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                parts = line.split(",")
                if len(parts) >= 2:
                    guid = parts[0]
                    name = parts[1]
                    inputs = {}

                    for input_pair in parts[2:]:
                        input_pair = input_pair.strip()
                        if ":" in input_pair:
                            key, value = input_pair.split(":", 1)
                            key = key.strip()
                            value = value.strip()

                            # Create Input object for each mapping
                            input_obj = Input.from_sdl_mapping(key, value)
                            if input_obj:
                                inputs[key] = input_obj

                    controllerdb[guid] = {
                        "guid": guid,
                        "name": name,
                        "inputs": inputs,
                        "type": "joystick",
                        "input_objects": inputs  # Backward compatible
                    }
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
        newController = _find_best_controller_config(controllers, str(i + 1), ci["guid"], ci["devicepath"])
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
        if controller['guid'] == pxguid:
            controller_data = controller.copy()
            controller_data["index"] = x
            controller_data["dev"] = pxdev
            return Controller.from_dict(controller_data)
    return None
