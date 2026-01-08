"""Controller database management.

Handles loading and matching controller configurations from gamecontrollerdb.txt.
"""

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from configgen.utils.logger import get_logger

from .controller import Controller, Input

eslog = get_logger(__name__)


def parse_line(line: str) -> tuple[str, dict[str, Any]] | None:
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


def _parse_chunk(lines: list[str]) -> dict[str, dict[str, Any]]:
    chunk_result: dict[str, dict[str, Any]] = {}
    for line in lines:
        parsed = parse_line(line)
        if parsed is None:
            continue
        guid, config = parsed
        chunk_result[guid] = config
    return chunk_result


def load_all_controllers_config() -> dict[str, dict[str, Any]]:
    """Load all controller configurations from gamecontrollerdb.txt, splitting the input evenly across available cores and parsing each slice in a thread pool."""
    controllerdb: dict[str, dict[str, Any]] = {}
    filepath = os.environ.get("SDL_GAMECONTROLLERCONFIG_FILE", "gamecontrollerdb.txt")

    try:
        with open(filepath, encoding="utf-8") as f:
            lines = f.read().splitlines()

        if not lines:
            return {}

        max_concurrency = max(1, os.cpu_count() or 1)
        chunk_size = max(1, (len(lines) + max_concurrency - 1) // max_concurrency)
        chunks = [lines[i : i + chunk_size] for i in range(0, len(lines), chunk_size)]
        worker_count = min(len(chunks), max_concurrency)

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            for chunk_result in executor.map(_parse_chunk, chunks):
                controllerdb.update(chunk_result)

    except FileNotFoundError:
        eslog.warning(f"Warning: Controller config file {filepath} not found.")
    except Exception as e:
        eslog.error(f"Error loading controller config: {e}")

    return controllerdb


def load_controller_config(
    controllersInput: list[dict[str, str]],
) -> dict[str, dict[str, Any]]:
    """Generate player-specific controller objects using the known controller database.

    Args:
        controllersInput (list): List of controller input descriptors containing "guid" and "devicepath".

    Returns:
        dict: Dictionary of Controller instances keyed by player number (as strings).

    """
    playerControllers: dict[str, dict[str, Any]] = {}
    controllers = load_all_controllers_config()

    for i, ci in enumerate(controllersInput):
        newController = _find_best_controller_config(
            controllers,
            str(i),
            ci["guid"],
            ci["devicepath"],
            ci["nbbuttons"],
            ci["nbhats"],
            ci["nbaxes"],
        )
        if newController:
            playerControllers[str(i + 1)] = newController
    return playerControllers


def _find_best_controller_config(
    controllers: dict[str, Any],
    x: str,
    pxguid: str,
    pxdev: str,
    pxbtns: str,
    pxhats: str,
    pxaxes: str,
) -> Any:
    """Find the best controller match in the loaded database by GUID and returns a Controller instance.

    Args:
        controllers (dict): Dictionary of available controller configurations.
        x (str): Player index (as string).
        pxguid (str): GUID of the connected controller.
        pxdev (str): Device path of the connected controller.
        pxbtns (str): Number of buttons on the controller.
        pxhats (str): Number of hats on the controller.
        pxaxes (str): Number of axes on the controller.

    Returns:
        Controller | None: Matched Controller instance or None if not found.

    """
    controller = controllers.get(pxguid)
    if not controller:
        return None
    controller_data = controller.copy()
    controller_data["index"] = x
    controller_data["dev"] = pxdev
    controller_data["nbbuttons"] = pxbtns
    controller_data["nbhats"] = pxhats
    controller_data["nbaxes"] = pxaxes
    return Controller.from_dict(controller_data)
