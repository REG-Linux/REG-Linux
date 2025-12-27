from pathlib import Path
from typing import Any

from configgen.systemFiles import CONF

CANNONBALL_CONFIG_PATH = str(Path(CONF) / "cannonball" / "config.xml")
CANNONBALL_BIN_PATH = "/usr/bin/cannonball"


def setCannonballConfig(cannoballConfig: Any, system: Any) -> None:
    # root
    xml_root = getRoot(cannoballConfig, "config")

    # video
    xml_video = getSection(cannoballConfig, xml_root, "video")

    # fps
    if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
        setSectionConfig(cannoballConfig, xml_video, "fps_counter", "1")
    else:
        setSectionConfig(cannoballConfig, xml_video, "fps_counter", "0")

    # ratio
    if system.isOptSet("ratio") and system.config["ratio"] == "16/9":
        setSectionConfig(cannoballConfig, xml_video, "widescreen", "1")
        setSectionConfig(cannoballConfig, xml_video, "mode", "1")
    else:
        setSectionConfig(cannoballConfig, xml_video, "widescreen", "0")
        setSectionConfig(cannoballConfig, xml_video, "mode", "1")

    # high resolution
    if system.isOptSet("highResolution") and system.config["highResolution"] == "1":
        setSectionConfig(cannoballConfig, xml_video, "hires", "1")
    else:
        setSectionConfig(cannoballConfig, xml_video, "hires", "0")


def getRoot(config: Any, name: str):
    xml_section = config.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        config.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section


def getSection(config: Any, xml_root: Any, name: str):
    xml_section = xml_root.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        xml_root.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section


def setSectionConfig(config: Any, xml_section: Any, name: str, value: str) -> None:
    xml_elt = xml_section.getElementsByTagName(name)
    if len(xml_elt) == 0:
        xml_elt = config.createElement(name)
        xml_section.appendChild(xml_elt)
    else:
        xml_elt = xml_elt[0]

    if xml_elt.hasChildNodes():
        xml_elt.firstChild.data = value
    else:
        xml_elt.appendChild(config.createTextNode(value))
