import xml.etree.ElementTree as ET
from .utils import shortNameFromPath
import systemFiles

from utils.logger import get_logger
eslog = get_logger(__name__)

def getGamesMetaData(system, rom):
    # load the database
    tree = ET.parse(systemFiles.esGamesMetadata)
    root = tree.getroot()
    game = shortNameFromPath(rom)
    res = {}
    eslog.info("looking for game metadata ({}, {})".format(system, game))

    targetSystem = system
    # hardcoded list of system for arcade
    # this list can be found in es_system.yml
    # at this stage we don't know if arcade will be kept as one system only in metadata, so i hardcode this list for now
    if system in ['naomi', 'naomi2', 'atomiswave', 'fbneo', 'mame', 'neogeo', 'triforce', 'hypseus-singe', 'model2', 'model3', 'hikaru', 'gaelco', 'cave3rd', 'namco2x6']:
        targetSystem = 'arcade'

    for nodesystem in root.findall(".//system"):
        system_names = nodesystem.get("name")
        if system_names is None:
            continue
        for sysname in system_names.split(','):
          if sysname == targetSystem:
              # search the game named default
              for nodegame in nodesystem.findall(".//game"):
                  if nodegame.get("name") == "default":
                      for child in nodegame:
                          for attribute in child.attrib:
                              key = "{}_{}".format(child.tag, attribute)
                              res[key] = child.get(attribute)
                              eslog.info("found game metadata {}={} (system level)".format(key, res[key]))
                      break
              for nodegame in nodesystem.findall(".//game"):
                  game_name = nodegame.get("name")
                  if game_name is not None and game_name != "default" and game_name in game:
                      for child in nodegame:
                          for attribute in child.attrib:
                              key = "{}_{}".format(child.tag, attribute)
                              res[key] = child.get(attribute)
                              eslog.info("found game metadata {}={}".format(key, res[key]))
                      return res
    return res

