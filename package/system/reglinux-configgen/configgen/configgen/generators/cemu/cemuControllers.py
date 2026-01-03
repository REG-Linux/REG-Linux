from os import mkdir, path, remove
from typing import Any
from xml.etree.ElementTree import Element, ElementTree, SubElement, indent


def setControllerConfig(system: Any, playersControllers: Any, profilesDir: str) -> None:
    # -= Wii U controller types =-
    GAMEPAD = "Wii U GamePad"
    PRO = "Wii U Pro Controller"
    CLASSIC = "Wii U Classic Controller"
    WIIMOTE = "Wiimote"

    API_SDL = "SDLController"

    DEFAULT_DEADZONE = "0.25"
    DEFAULT_RANGE = "1"

    BUTTON_MAPPINGS = {
        GAMEPAD: {  # excludes show screen
            "1": "1",
            "2": "0",
            "3": "3",
            "4": "2",
            "5": "9",
            "6": "10",
            "7": "42",
            "8": "43",
            "9": "6",
            "10": "4",
            "11": "11",
            "12": "12",
            "13": "13",
            "14": "14",
            "15": "7",
            "16": "8",
            "17": "45",
            "18": "39",
            "19": "44",
            "20": "38",
            "21": "47",
            "22": "41",
            "23": "46",
            "24": "40",
            "25": "7",
        },
        PRO: {
            "1": "1",
            "2": "0",
            "3": "3",
            "4": "2",
            "5": "9",
            "6": "10",
            "7": "42",
            "8": "43",
            "9": "6",
            "10": "4",
            # 11 is excluded
            "12": "11",
            "13": "12",
            "14": "13",
            "15": "14",
            "16": "7",
            "17": "8",
            "18": "45",
            "19": "39",
            "20": "44",
            "21": "38",
            "22": "47",
            "23": "41",
            "24": "46",
            "25": "40",
        },
        CLASSIC: {
            "1": "13",
            "2": "12",
            "3": "15",
            "4": "14",
            "5": "8",
            "6": "9",
            "7": "42",
            "8": "43",
            "9": "4",
            "10": "5",
            # 11 is excluded
            "12": "0",
            "13": "1",
            "14": "2",
            "15": "3",
            "16": "39",
            "17": "45",
            "18": "44",
            "19": "38",
            "20": "41",
            "21": "47",
            "22": "46",
            "23": "40",
        },
        WIIMOTE: {  # with MotionPlus & Nunchuck, excludes Home button
            "1": "0",
            "2": "43",
            "3": "2",
            "4": "1",
            "5": "42",
            "6": "9",
            "7": "6",
            "8": "4",
            "9": "11",
            "10": "12",
            "11": "13",
            "12": "14",
            "13": "45",
            "14": "39",
            "15": "44",
            "16": "38",
        },
    }

    def getOption(option: str, defaultValue: Any) -> Any:
        if system.isOptSet(option):
            return system.config[option]
        return defaultValue

    def addTextElement(parent: Any, name: str, value: str) -> Any:
        element = SubElement(parent, name)
        element.text = value

    def addAnalogControl(parent: Any, name: str) -> None:
        element = SubElement(parent, name)
        addTextElement(element, "deadzone", DEFAULT_DEADZONE)
        addTextElement(element, "range", DEFAULT_RANGE)

    def getConfigFileName(controller: Any) -> str:
        return path.join(profilesDir, f"controller{controller}.xml")

    # Make controller directory if it doesn't exist
    if not path.isdir(profilesDir):
        mkdir(profilesDir)

    # Purge old controller files
    for counter in range(8):
        configFileName = getConfigFileName(counter)
        if path.isfile(configFileName):
            remove(configFileName)

    ## CONTROLLER: Create the config xml files
    nplayer = 0

    # cemu assign pads by uuid then by index with the same uuid
    # so, if 2 pads have the same uuid, the index is not 0 but 1 for the 2nd one
    # sort pads by index
    pads_by_index = dict(sorted(playersControllers.items(), key=lambda kv: kv[1].index))
    guid_n = {}
    guid_count = {}
    for pad in pads_by_index.values():
        if pad.guid in guid_count:
            guid_count[pad.guid] += 1
        else:
            guid_count[pad.guid] = 0
        guid_n[pad.index] = guid_count[pad.guid]
    ###

    for nplayer, pad in enumerate(pads_by_index.values()):
        root = Element("emulated_controller")

        # Set type from controller combination
        type = PRO  # default
        if (
            system.isOptSet("cemu_controller_combination")
            and system.config["cemu_controller_combination"] != "0"
        ):
            if system.config["cemu_controller_combination"] == "1":
                type = GAMEPAD if nplayer == 0 else WIIMOTE
            elif system.config["cemu_controller_combination"] == "2":
                type = PRO
            else:
                type = WIIMOTE
            if system.config["cemu_controller_combination"] == "4":
                type = CLASSIC
        else:
            type = GAMEPAD if nplayer == 0 else PRO
        addTextElement(root, "type", type)

        # Create controller configuration
        controllerNode = SubElement(root, "controller")
        addTextElement(controllerNode, "api", API_SDL)
        addTextElement(
            controllerNode, "uuid", f"{guid_n[pad.index]}_{pad.guid}",
        )  # controller guid
        addTextElement(controllerNode, "display_name", pad.name)  # controller name
        addTextElement(
            controllerNode, "rumble", getOption("cemu_rumble", "0"),
        )  # % chosen
        addAnalogControl(controllerNode, "axis")
        addAnalogControl(controllerNode, "rotation")
        addAnalogControl(controllerNode, "trigger")

        # Apply the appropriate button mappings
        mappingsNode = SubElement(controllerNode, "mappings")
        for key, value in BUTTON_MAPPINGS[type].items():
            entryNode = SubElement(mappingsNode, "entry")
            addTextElement(entryNode, "mapping", key)
            addTextElement(entryNode, "button", value)

        # Save to file
        with open(getConfigFileName(nplayer), "wb") as handle:
            tree = ElementTree(root)
            indent(tree, space="  ", level=0)
            tree.write(handle, encoding="UTF-8", xml_declaration=True)
            handle.close()
