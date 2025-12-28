import xml.etree.ElementTree as ET
from typing import Any

from configgen.systemFiles import ES_GAMES_METADATA
from configgen.utils.logger import get_logger

from .utils import shortNameFromPath

eslog = get_logger(__name__)


def getGamesMetaData(system: Any, rom: str) -> dict[str, Any]:
    # load the database
    tree = ET.parse(ES_GAMES_METADATA)
    root = tree.getroot()
    game = shortNameFromPath(rom)
    res = {}
    eslog.info(f"looking for game metadata ({system}, {game})")

    targetSystem = system
    # hardcoded list of system for arcade
    # this list can be found in es_system.yml
    # at this stage we don't know if arcade will be kept as one system only in metadata, so i hardcode this list for now
    if system in [
        "naomi",
        "naomi2",
        "atomiswave",
        "fbneo",
        "mame",
        "neogeo",
        "triforce",
        "hypseus-singe",
        "model3",
        "hikaru",
        "gaelco",
        "cave3rd",
        "namco2x6",
    ]:
        targetSystem = "arcade"

    for nodesystem in root.findall(".//system"):
        system_names = nodesystem.get("name")
        if system_names is None:
            continue
        for sysname in system_names.split(","):
            if sysname == targetSystem:
                # search the game named default
                for nodegame in nodesystem.findall(".//game"):
                    if nodegame.get("name") == "default":
                        for child in nodegame:
                            for attribute in child.attrib:
                                key = f"{child.tag}_{attribute}"
                                res[key] = child.get(attribute)
                                eslog.info(
                                    f"found game metadata {key}={res[key]} (system level)"
                                )
                        break
                for nodegame in nodesystem.findall(".//game"):
                    game_name = nodegame.get("name")
                    if (
                        game_name is not None
                        and game_name != "default"
                        and game_name in game
                    ):
                        for child in nodegame:
                            for attribute in child.attrib:
                                key = f"{child.tag}_{attribute}"
                                res[key] = child.get(attribute)
                                eslog.info(f"found game metadata {key}={res[key]}")
                        return res
    return res
