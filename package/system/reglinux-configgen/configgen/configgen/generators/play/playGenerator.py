from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path, makedirs
from xml.etree.ElementTree import Element, SubElement, ElementTree, parse
from configgen.systemFiles import CONF, SAVES

PLAY_CONFIG_DIR = CONF + "/play"
PLAY_SAVE_DIR = SAVES + "/play"
PLAY_HOME_DIR = CONF
PLAY_BIN_PATH = "/usr/bin/Play"
PLAY_CONFIG_FILE = PLAY_CONFIG_DIR + "/Play Data Files/config.xml"
PLAY_INPUT_FILE = PLAY_CONFIG_DIR + "/Play Data Files/inputprofiles/default.xml"


class PlayGenerator(Generator):
    # Play is QT6 based, requires wayland compositor to run
    def requiresWayland(self):
        return True

    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # Create config folder
        if not path.isdir(PLAY_CONFIG_DIR):
            makedirs(PLAY_CONFIG_DIR)
        # Create save folder
        if not path.isdir(PLAY_SAVE_DIR):
            makedirs(PLAY_SAVE_DIR)

        ## Work with the config.xml file
        root = Element("Config")

        # Dictionary of preferences and defaults
        preferences = {
            "ps2.arcaderoms.directory": {
                "Type": "path",
                "Value": "/userdata/roms/namco2x6",
            },
            "ui.showexitconfirmation": {"Type": "boolean", "Value": "false"},
            "ui.pausewhenfocuslost": {"Type": "boolean", "Value": "false"},
            "ui.showeecpuusage": {"Type": "boolean", "Value": "false"},
            "ps2.limitframerate": {"Type": "boolean", "Value": "true"},
            "renderer.widescreen": {"Type": "boolean", "Value": "false"},
            "system.language": {"Type": "integer", "Value": "1"},
            "video.gshandler": {"Type": "integer", "Value": "0"},
            "renderer.opengl.resfactor": {"Type": "integer", "Value": "1"},
            "renderer.presentationmode": {"Type": "integer", "Value": "1"},
            "renderer.opengl.forcebilineartextures": {
                "Type": "boolean",
                "Value": "false",
            },
        }

        # Check if the file exists
        if path.exists(PLAY_CONFIG_FILE):
            tree = parse(PLAY_CONFIG_FILE)
            root = tree.getroot()
        # Add or update preferences
        for pref_name, pref_attrs in preferences.items():
            pref_element = root.find(f".//Preference[@Name='{pref_name}']")
            if pref_element is None:
                # Preference doesn't exist, create a new element
                pref_element = SubElement(root, "Preference")
                pref_element.attrib["Name"] = pref_name
            # Set or update attribute values
            for attr_name, attr_value in pref_attrs.items():
                pref_element.attrib[attr_name] = attr_value
                # User options
                if pref_name == "ps2.limitframerate" and system.isOptSet("play_vsync"):
                    pref_element.attrib["Value"] = system.config["play_vsync"]
                if pref_name == "renderer.widescreen" and system.isOptSet(
                    "play_widescreen"
                ):
                    pref_element.attrib["Value"] = system.config["play_widescreen"]
                if pref_name == "system.language" and system.isOptSet("play_language"):
                    pref_element.attrib["Value"] = system.config["play_language"]
                if pref_name == "video.gshandler" and system.isOptSet("play_api"):
                    pref_element.attrib["Value"] = system.config["play_api"]
                if pref_name == "renderer.opengl.resfactor" and system.isOptSet(
                    "play_scale"
                ):
                    pref_element.attrib["Value"] = system.config["play_scale"]
                if pref_name == "renderer.presentationmode" and system.isOptSet(
                    "play_mode"
                ):
                    pref_element.attrib["Value"] = system.config["play_mode"]
                if (
                    pref_name == "renderer.opengl.forcebilineartextures"
                    and system.isOptSet("play_filter")
                ):
                    pref_element.attrib["Value"] = system.config["play_filter"]

        # Create the tree and write to the file
        tree = ElementTree(root)

        # Handle the case when the file doesn't exist
        if not path.exists(PLAY_CONFIG_FILE):
            # Create the directory if it doesn't exist
            directory = path.dirname(PLAY_CONFIG_FILE)
            makedirs(directory, exist_ok=True)
            # Write the XML to the file
            tree.write(PLAY_CONFIG_FILE)
        else:
            # File exists, write the XML to the existing file
            with open(PLAY_CONFIG_FILE, "wb") as file:
                tree.write(file)

        command_array = [PLAY_BIN_PATH, "--fullscreen"]

        if rom != "config":
            # if zip, it's a namco arcade game
            if rom.lower().endswith("zip"):
                # strip path & extension
                rom = path.basename(rom)
                rom = path.splitext(rom)[0]
                command_array.extend(["--arcade", rom])
            else:
                command_array.extend(["--disc", rom])

        return Command(array=command_array)

    def get_in_game_ratio(self, config, game_resolution, rom):
        if "play_widescreen" in config and config["play_widescreen"] == "true":
            return 16 / 9
        elif "play_mode" in config and config["play_mode"] == "0":
            return 16 / 9
        else:
            return 4 / 3
