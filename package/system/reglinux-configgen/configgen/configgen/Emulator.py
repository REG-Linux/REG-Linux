#!/usr/bin/env python3

import os
import systemFiles
import xml.etree.ElementTree as ET
import yaml
from typing import Dict, Any
from settings.unixSettings import UnixSettings

from utils.logger import get_logger
eslog = get_logger(__name__)

class Emulator:
    """Manages emulator configurations for a given system and ROM in a RegLinux environment.

    This class loads and merges configuration settings from YAML files, system.conf, and
    EmulationStation settings, handling emulator, core, and rendering options.

    Attributes:
        name (str): The name of the system (e.g., 'nes', 'snes').
        config (Dict[str, Any]): Configuration dictionary for the emulator and options.
        renderconfig (Dict[str, Any]): Rendering configuration (e.g., shaders).
    """

    def __init__(self, name: str, rom: str):
        """Initialize the emulator with system name and ROM path.

        Args:
            name (str): The system name (e.g., 'nes', 'snes').
            rom (str): Path to the ROM file.

        Raises:
            Exception: If no emulator is defined in the configuration.
        """
        self.name = name

        # Load system configuration from default YAML files
        self.config = Emulator.get_system_config(
            self.name,
            "/usr/share/reglinux/configgen/configgen-defaults.yml",
            "/usr/share/reglinux/configgen/configgen-defaults-arch.yml"
        )
        if "emulator" not in self.config or self.config["emulator"] == "":
            eslog.error("No emulator defined. Exiting.")
            raise Exception("No emulator found")

        # Get sanitized game settings name from ROM
        gsname = self.game_settings_name(rom)

        # Load configurations from system.conf using UnixSettings
        recalSettings = UnixSettings(systemFiles.systemConf)
        globalSettings = recalSettings.loadAll('global')
        controllersSettings = recalSettings.loadAll('controllers', True)
        systemSettings = recalSettings.loadAll(self.name)
        folderSettings = recalSettings.loadAll(self.name + ".folder[\"" + os.path.dirname(rom) + "\"]")
        gameSettings = recalSettings.loadAll(self.name + "[\"" + gsname + "\"]")

        # Add display settings to config
        displaySettings = recalSettings.loadAll('display')
        for opt in displaySettings:
            self.config["display." + opt] = displaySettings[opt]

        # Update config with settings in order of precedence
        Emulator.updateConfiguration(self.config, controllersSettings)
        Emulator.updateConfiguration(self.config, globalSettings)
        Emulator.updateConfiguration(self.config, systemSettings)
        Emulator.updateConfiguration(self.config, folderSettings)
        Emulator.updateConfiguration(self.config, gameSettings)
        self.updateFromESSettings()
        eslog.debug(f"uimode: {self.config['uimode']}")

        # Check if emulator or core is forcibly set
        self.config["emulator-forced"] = False
        self.config["core-forced"] = False
        if "emulator" in globalSettings or "emulator" in systemSettings or "emulator" in gameSettings:
            self.config["emulator-forced"] = True
        if "core" in globalSettings or "core" in systemSettings or "core" in gameSettings:
            self.config["core-forced"] = True

        # Initialize renderconfig for shaders
        self.renderconfig = {}
        if "shaderset" in self.config:
            if self.config["shaderset"] != "none":
                # Prefer user-defined shader configs if available
                if os.path.exists("/userdata/shaders/configs/" + self.config["shaderset"] + "/rendering-defaults.yml"):
                    self.renderconfig = Emulator.get_generic_config(
                        self.name,
                        "/userdata/shaders/configs/" + self.config["shaderset"] + "/rendering-defaults.yml",
                        "/userdata/shaders/configs/" + self.config["shaderset"] + "/rendering-defaults-arch.yml"
                    )
                else:
                    self.renderconfig = Emulator.get_generic_config(
                        self.name,
                        "/usr/share/reglinux/shaders/configs/" + self.config["shaderset"] + "/rendering-defaults.yml",
                        "/usr/share/reglinux/shaders/configs/" + self.config["shaderset"] + "/rendering-defaults-arch.yml"
                    )
            elif self.config["shaderset"] == "none":
                # Use default rendering configs if no shaders are set
                self.renderconfig = Emulator.get_generic_config(
                    self.name,
                    "/usr/share/reglinux/shaders/configs/rendering-defaults.yml",
                    "/usr/share/reglinux/shaders/configs/rendering-defaults-arch.yml"
                )

        # Load renderer-specific settings for backward compatibility
        systemSettings = recalSettings.loadAll(self.name + "-renderer")
        gameSettings = recalSettings.loadAll(self.name + "[\"" + gsname + "\"]" + "-renderer")

        # Update renderconfig with renderer settings
        Emulator.updateConfiguration(self.renderconfig, systemSettings)
        Emulator.updateConfiguration(self.renderconfig, gameSettings)

    def game_settings_name(self, rom: str) -> str:
        """Generate a sanitized game settings name from the ROM file name.

        Args:
            rom (str): Path to the ROM file.

        Returns:
            str: Sanitized game settings name compatible with EmulationStation.
        """
        rom = os.path.basename(rom)

        # Sanitize name by removing invalid characters per EmulationStation rules
        rom = rom.replace('=', '').replace('#', '')
        eslog.info(f"game settings name: {rom}")
        return rom

    @staticmethod
    def dict_merge(dct: Dict[Any, Any], merge_dct: Dict[Any, Any]) -> None:
        """Recursively merge merge_dct into dct, updating nested dictionaries.

        Args:
            dct: The dictionary to update.
            merge_dct: The dictionary to merge into dct.
        """
        for key, value in merge_dct.items():
            if key in dct and isinstance(dct[key], dict) and isinstance(value, dict):
                Emulator.dict_merge(dct[key], value)
            else:
                dct[key] = value

    @staticmethod
    def get_generic_config(system: str, defaultyml: str, defaultarchyml: str) -> Dict[str, Any]:
        """Load and merge generic configuration from YAML files.

        Args:
            system (str): The system name (e.g., 'nes', 'snes').
            defaultyml (str): Path to the default YAML configuration file.
            defaultarchyml (str): Path to the architecture-specific YAML configuration file.

        Returns:
            Dict[str, Any]: Merged configuration dictionary.
        """
        # Load default configuration
        with open(defaultyml, 'r') as f:
            systems_default = yaml.load(f, Loader=yaml.SafeLoader)

        # Load architecture-specific configuration if available
        systems_default_arch = {}
        if os.path.exists(defaultarchyml):
            with open(defaultarchyml, 'r') as f:
                systems_default_arch = yaml.load(f, Loader=yaml.SafeLoader) or {}

        dict_all: Dict[str, Any] = {}

        # Merge default configurations
        if "default" in systems_default:
            dict_all = systems_default["default"]

        if "default" in systems_default_arch:
            Emulator.dict_merge(dict_all, systems_default_arch["default"])

        # Merge system-specific configurations
        if system in systems_default:
            Emulator.dict_merge(dict_all, systems_default[system])

        if system in systems_default_arch:
            Emulator.dict_merge(dict_all, systems_default_arch[system])

        return dict_all

    @staticmethod
    def get_system_config(system: str, defaultyml: str, defaultarchyml: str) -> Dict[str, Any]:
        """Load system-specific configuration, including emulator and core settings.

        Args:
            system (str): The system name (e.g., 'nes', 'snes').
            defaultyml (str): Path to the default YAML configuration file.
            defaultarchyml (str): Path to the architecture-specific YAML configuration file.

        Returns:
            Dict[str, Any]: System configuration dictionary with emulator, core, and options.
        """
        dict_all = Emulator.get_generic_config(system, defaultyml, defaultarchyml)

        # Extract emulator and core, merge options
        dict_result = {"emulator": dict_all["emulator"], "core": dict_all["core"]}
        if "options" in dict_all:
            Emulator.dict_merge(dict_result, dict_all["options"])
        return dict_result

    def isOptSet(self, key: str) -> bool:
        """Check if a configuration option is set.

        Args:
            key (str): The configuration option key.

        Returns:
            bool: True if the key exists in the config, False otherwise.
        """
        return key in self.config

    def getOptBoolean(self, key: str) -> bool:
        """Get a configuration option as a boolean value.

        Args:
            key (str): The configuration option key.

        Returns:
            bool: True if the option is set to a truthy value, False otherwise.
        """
        true_values = {'1', 'true', 'on', 'enabled', True}
        value = self.config.get(key)

        if isinstance(value, str):
            value = value.lower()

        return value in true_values

    def getOptString(self, key: str) -> str:
        """Get a configuration option as a string.

        Args:
            key (str): The configuration option key.

        Returns:
            str: The option value as a string, or empty string if not set.
        """
        return str(self.config.get(key, ""))

    @staticmethod
    def updateConfiguration(config: Dict[str, Any], settings: Dict[str, Any]) -> None:
        """Update a configuration dictionary with new settings, ignoring invalid values.

        Args:
            config (Dict[str, Any]): The configuration dictionary to update.
            settings (Dict[str, Any]): The new settings to apply.
        """
        # Remove invalid settings ("default", "auto", or empty)
        toremove = [k for k in settings if settings[k] in ("", "default", "auto")]
        for k in toremove:
            del settings[k]

        config.update(settings)

    def updateFromESSettings(self) -> None:
        """Update emulator config with settings from EmulationStation XML file.

        Reads settings like showFPS and uimode from the EmulationStation configuration.
        Sets default values if the file is unavailable or parsing fails.
        """
        try:
            esConfig = ET.parse(systemFiles.esSettings)

            # Read showFPS setting
            drawframerate_elem = esConfig.find("./bool[@name='DrawFramerate']")
            if drawframerate_elem is not None:
                drawframerate_value = drawframerate_elem.attrib.get("value", "false")
            else:
                drawframerate_value = "false"
            if drawframerate_value not in ['false', 'true']:
                drawframerate_value = 'false'
            self.config['showFPS'] = drawframerate_value

            # Read uimode setting
            uimode_elem = esConfig.find("./string[@name='UIMode']")
            if uimode_elem is not None:
                uimode_value = uimode_elem.attrib.get("value", "Full")
            else:
                uimode_value = "Full"
            if uimode_value not in ['Full', 'Kiosk', 'Kid']:
                uimode_value = 'Full'
            self.config['uimode'] = uimode_value

        except Exception:
            # Use defaults if ES settings cannot be loaded
            self.config['showFPS'] = "false"
            self.config['uimode'] = "Full"
