
import os
from controllers import Controller

# Load all controllers from the gamecontrollerdb.txt
def loadAllControllersConfig():
    controllerdb = dict()
    filepath = os.environ.get("SDL_GAMECONTROLLERCONFIG_FILE", "gamecontrollerdb.txt")
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
                    inputs_str = parts[2:]
                    inputs = {}

                    for input_pair in inputs_str:
                        input_pair = input_pair.strip()
                        if ":" in input_pair:
                            key, value = input_pair.split(":", 1)
                            inputs[key.strip()] = value.strip()

                    controllerdb[guid] = {
                        "guid": guid,
                        "name": name,
                        "inputs": inputs,
                        "type": "gamepad"
                    }
    except FileNotFoundError:
        print(f"File {filepath} not found.")
    return controllerdb

# Create a controller array with the player id as a key
def loadControllerConfig(controllersInput):
    playerControllers = dict()
    controllers = loadAllControllersConfig()

    for i, ci in enumerate(controllersInput):
        newController = findBestControllerConfig(controllers, str(i+1), ci["guid"], ci["devicepath"])
        if newController:
            playerControllers[str(i+1)] = newController
    return playerControllers

def findBestControllerConfig(controllers, x, pxguid, pxdev):
    for controllerGUID in controllers:
        controller = controllers[controllerGUID]
        if controller['guid'] == pxguid:
            return Controller(controller['guid'], controller['name'], controller['inputs'], controller['type'], x, pxdev)
    return None
