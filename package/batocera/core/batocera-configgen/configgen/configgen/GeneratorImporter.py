#!/usr/bin/env python3

import importlib
import os

# Dictionary mapping emulator names to their generator class paths
global GENERATOR_MAP
GENERATOR_MAP = {}

def generate_generator_map(base_path='generators'):
    """
    Dynamically populates the GENERATOR_MAP dictionary based on the directory structure.

    It scans the 'generators/' directory recursively, finds all files ending in 'Generator.py',
    and maps their containing folder (used as emulator name) to the fully-qualified class path.

    Emulator folder names with underscores are converted to hyphens for uniformity.
    The resulting map is sorted alphabetically by emulator name.
    """
    global GENERATOR_MAP
    temp_map = {}
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith("Generator.py") and not file.startswith("__"):
                rel_path = os.path.join(root, file).replace(os.sep, ".")
                module_path = rel_path[:-3]  # remove .py extension
                class_name = file[:-3]       # remove .py extension
                emulator = os.path.basename(root).replace("_", "-")  # normalize names
                temp_map[emulator] = f"{module_path}.{class_name}"

    # Sort the dictionary alphabetically by emulator name
    GENERATOR_MAP = dict(sorted(temp_map.items()))

def getGenerator(emulator):
    """
    Returns an instance of the generator class corresponding to the given emulator name.

    If the map is empty, it will be auto-generated from the directory structure.
    Raises an exception if the emulator is not supported or the module/class cannot be loaded.

    Args:
        emulator (str): The emulator identifier (e.g., 'libretro', 'dolphin', etc.)

    Returns:
        object: An instance of the appropriate generator class
    """
    try:
        if not GENERATOR_MAP:
            generate_generator_map()
        module_path, class_name = GENERATOR_MAP[emulator].rsplit('.', 1)
        module = importlib.import_module(module_path)
        return getattr(module, class_name)()
    except KeyError:
        raise Exception(f"No generator found for emulator '{emulator}'")
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Failed to load generator for emulator '{emulator}': {e}")
