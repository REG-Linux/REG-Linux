from systemFiles import CONF

CANNONBALL_CONFIG_PATH = CONF + '/cannonball/config.xml'
CANNONBALL_BIN_PATH = '/usr/bin/cannonball'

def setCannonballConfig(cannoballConfig, system):
    # root
    xml_root = getRoot(cannoballConfig, "config")

    # video
    xml_video = getSection(cannoballConfig, xml_root, "video")

    # fps
    if system.isOptSet('showFPS') and system.getOptBoolean('showFPS'):
        setSectionConfig(cannoballConfig, xml_video, "fps_counter", "1")
    else:
        setSectionConfig(cannoballConfig, xml_video, "fps_counter", "0")

    # ratio
    if system.isOptSet('ratio') and system.config["ratio"] == "16/9":
        setSectionConfig(cannoballConfig, xml_video, "widescreen", "1")
        setSectionConfig(cannoballConfig, xml_video, "mode", "1")
    else:
        setSectionConfig(cannoballConfig, xml_video, "widescreen", "0")
        setSectionConfig(cannoballConfig, xml_video, "mode", "1")

    # high resolution
    if system.isOptSet('highResolution') and system.config["highResolution"] == "1":
        setSectionConfig(cannoballConfig, xml_video, "hires", "1")
    else:
        setSectionConfig(cannoballConfig, xml_video, "hires", "0")


@staticmethod
def getRoot(config, name):
    xml_section = config.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        config.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section

@staticmethod
def getSection(config, xml_root, name):
    xml_section = xml_root.getElementsByTagName(name)

    if len(xml_section) == 0:
        xml_section = config.createElement(name)
        xml_root.appendChild(xml_section)
    else:
        xml_section = xml_section[0]

    return xml_section

@staticmethod
def setSectionConfig(config, xml_section, name, value):
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
