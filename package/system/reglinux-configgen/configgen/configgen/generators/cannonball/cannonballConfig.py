import os
import codecs
from xml.dom import minidom
from systemFiles import CONF

cannonballConfigFile = CONF + '/cannonball/config.xml'
cannonballBin = "/usr/bin/cannonball"

def setCannonballConfig(system):
    if not os.path.exists(os.path.dirname(cannonballConfigFile)):
        os.makedirs(os.path.dirname(cannonballConfigFile))

    # config file
    config = minidom.Document()
    if os.path.exists(cannonballConfigFile):
        try:
            config = minidom.parse(cannonballConfigFile)
        except:
            pass # reinit the file

    # root
    xml_root = getRoot(config, "config")

    # video
    xml_video = getSection(config, xml_root, "video")

    # fps
    if system.isOptSet('showFPS') and system.getOptBoolean('showFPS'):
        setSectionConfig(config, xml_video, "fps_counter", "1")
    else:
        setSectionConfig(config, xml_video, "fps_counter", "0")

    # ratio
    if system.isOptSet('ratio') and system.config["ratio"] == "16/9":
        setSectionConfig(config, xml_video, "widescreen", "1")
        setSectionConfig(config, xml_video, "mode", "1")
    else:
        setSectionConfig(config, xml_video, "widescreen", "0")
        setSectionConfig(config, xml_video, "mode", "1")

    # high resolution
    if system.isOptSet('highResolution') and system.config["highResolution"] == "1":
        setSectionConfig(config, xml_video, "hires", "1")
    else:
        setSectionConfig(config, xml_video, "hires", "0")

    # save the config file
    cannonballXml = codecs.open(cannonballConfigFile, "w", "utf-8")
    dom_string = os.linesep.join([s for s in config.toprettyxml().splitlines() if s.strip()]) # remove ugly empty lines while minicom adds them...
    cannonballXml.write(dom_string)
    cannonballXml.close()

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
