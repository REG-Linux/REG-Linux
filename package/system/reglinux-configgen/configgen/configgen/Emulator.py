import xml.etree.ElementTree as ET
from os import path
from typing import Any

import yaml
from yaml import CLoader as Loader

try:
    from typing import TypedDict
except ImportError:
    pass

# Import with fallback for different execution contexts
try:
    from configgen.systemFiles import ES_SETTINGS, SYSTEM_CONF
except ImportError:
    # When run as a module within the package
    from .systemFiles import ES_SETTINGS, SYSTEM_CONF

try:
    from configgen.settings import UnixSettings
except ImportError:
    # When run as a module within the package
    from .settings import UnixSettings

try:
    from configgen.utils.logger import get_logger
except ImportError:
    # When run as a module within the package
    from .utils.logger import get_logger

eslog = get_logger(__name__)


# Defining TypedDicts for configuration structures
class SystemConfigRequired(TypedDict, total=True):
    """Required fields in SystemConfig"""

    emulator: str
    core: str


class SystemConfigOptional(TypedDict, total=False):
    """Optional fields in SystemConfig"""

    videomode: str
    showFPS: str
    uimode: str
    bezel: str
    gun_cursor: str
    gun_delay: str
    vkeyboard: str
    # Retroachievements options
    retroachievements: str
    retroachievements_hardcore: str
    retroachievements_leaderboards: str
    retroachievements_verbose: str
    retroachievements_automatic_screenshot: str
    retroachievements_challenge_indicators: str
    retroachievements_play_sounds: str
    retroachievements_menu_enable: str
    retroachievements_unofficial: str
    retroachievements_use_ranked_assets: str
    retroachievements_show_lboard_ui: str
    retroachievements_start_active: str
    retroachievements_richpresence: str
    retroachievements_encore: str
    retroachievements_spectator: str
    retroachievements_screenshot: str
    # Other options
    force_module: str
    disableautocontrollers: str
    ratio: str
    smoothing: str
    rewind: str
    autosave: str
    shufflesongs: str
    pixel_perfect: str
    stretch: str
    game_translation: str
    game_focus: str
    cheevos_game_id: str
    # Video options
    video_threaded: str
    video_shared_context: str
    video_vsync: str
    video_smooth: str
    video_scale_integer: str
    video_fullscreen: str
    video_windowed_fullscreen: str
    # Common options
    audio_dsp_plugin: str
    audio_driver: str
    input_driver: str
    cheevos_password: str | None
    # SDL options
    sdlvsync: str
    # Special runtime properties
    emulator_forced: bool
    core_forced: bool


class SystemConfig(SystemConfigRequired, SystemConfigOptional):
    """System configuration with required and optional fields"""

    pass


class RenderConfig(TypedDict, total=False):
    shader: str
    smooth: str
    rewind: str
    autosave: str
    shufflesongs: str
    pixel_perfect: str
    stretch: str
    ratio: str


# Define a flexible config type that can accept additional keys
# Using Dict[str, Any] directly since the config is dynamically modified
SystemConfigDict = dict[str, Any]
RenderConfigDict = dict[str, Any]


class Emulator:
    """Manages emulator configurations for a given system and ROM in a RegLinux environment.

    This class loads and merges configuration settings from YAML files, system.conf, and
    EmulationStation settings, handling emulator, core, and rendering options.

    Attributes:
        name: The name of the system (e.g., 'nes', 'snes').
        config: Configuration dictionary for the emulator and options.
        renderconfig: Rendering configuration (e.g., shaders).
    """

    def __init__(self, name: str, rom: str) -> None:
        """Initialize the emulator with system name and ROM path.

        Args:
            name: The system name (e.g., 'nes', 'snes').
            rom: Path to the ROM file.

        Raises:
            Exception: If no emulator is defined in the configuration.
        """
        self.name: str = name
        self.rom: str = rom
        self.config: SystemConfigDict = {}
        self.renderconfig: dict[str, Any] = {}

        # Load system configuration from default YAML files
        self.config = Emulator.get_system_config(
            self.name,
            "/usr/share/reglinux/configgen/configgen-defaults.yml",
            "/usr/share/reglinux/configgen/configgen-defaults-arch.yml",
        )
        if "emulator" not in self.config or self.config["emulator"] == "":
            eslog.error("No emulator defined. Exiting.")
            raise Exception("No emulator found")

        # Get sanitized game settings name from ROM
        gsname = self.game_settings_name(rom)

        # Load configurations from system.conf using UnixSettings
        recalSettings = UnixSettings(SYSTEM_CONF)
        globalSettings = recalSettings.loadAll("global")
        controllersSettings = recalSettings.loadAll("controllers", True)
        systemSettings = recalSettings.loadAll(self.name)
        folderSettings = recalSettings.loadAll(
            self.name + '.folder["' + path.dirname(rom) + '"]'
        )
        gameSettings = recalSettings.loadAll(self.name + '["' + gsname + '"]')

        # Add display settings to config
        displaySettings = recalSettings.loadAll("display")
        for opt in displaySettings:
            self.config["display." + opt] = displaySettings[opt]  # type: ignore

        # Update config with settings in order of precedence
        Emulator.updateConfiguration(self.config, controllersSettings)
        Emulator.updateConfiguration(self.config, globalSettings)
        Emulator.updateConfiguration(self.config, systemSettings)
        Emulator.updateConfiguration(self.config, folderSettings)
        Emulator.updateConfiguration(self.config, gameSettings)
        self.updateFromESSettings()
        eslog.debug(f"uimode: {self.config.get('uimode')}")

        # Check if emulator or core is forcibly set
        self.config["emulator_forced"] = False
        self.config["core_forced"] = False
        if (
            "emulator" in globalSettings
            or "emulator" in systemSettings
            or "emulator" in gameSettings
        ):
            self.config["emulator_forced"] = True
        if (
            "core" in globalSettings
            or "core" in systemSettings
            or "core" in gameSettings
        ):
            self.config["core_forced"] = True

        # Initialize renderconfig for shaders
        self.renderconfig = {}
        if "shaderset" in self.config:
            shaderset = self.config["shaderset"]
            if shaderset != "none":
                # Prefer user-defined shader configs if available
                user_shader_path = (
                    f"/userdata/shaders/configs/{shaderset}/rendering-defaults.yml"
                )
                if path.exists(user_shader_path):
                    self.renderconfig = Emulator.get_generic_config(
                        self.name,
                        user_shader_path,
                        f"/userdata/shaders/configs/{shaderset}/rendering-defaults-arch.yml",
                    )
                else:
                    self.renderconfig = Emulator.get_generic_config(
                        self.name,
                        f"/usr/share/reglinux/shaders/configs/{shaderset}/rendering-defaults.yml",
                        f"/usr/share/reglinux/shaders/configs/{shaderset}/rendering-defaults-arch.yml",
                    )
            elif shaderset == "none":
                # Use default rendering configs if no shaders are set
                self.renderconfig = Emulator.get_generic_config(
                    self.name,
                    "/usr/share/reglinux/shaders/configs/rendering-defaults.yml",
                    "/usr/share/reglinux/shaders/configs/rendering-defaults-arch.yml",
                )

        # Load renderer-specific settings for backward compatibility
        systemSettings = recalSettings.loadAll(self.name + "-renderer")
        gameSettings = recalSettings.loadAll(
            self.name + '["' + gsname + '"]' + "-renderer"
        )

        # Update renderconfig with renderer settings
        Emulator.updateConfiguration(self.renderconfig, systemSettings)
        Emulator.updateConfiguration(self.renderconfig, gameSettings)

    def game_settings_name(self, rom: str) -> str:
        """Generate a sanitized game settings name from the ROM file name.

        Args:
            rom: Path to the ROM file.

        Returns:
            Sanitized game settings name compatible with EmulationStation.
        """
        rom = path.basename(rom)

        # Sanitize name by removing invalid characters per EmulationStation rules
        # Using walrus operator for assignment expressions where useful
        if "=" in rom or "#" in rom:
            rom = rom.replace("=", "").replace("#", "")

        eslog.info(f"game settings name: {rom}")
        return rom

    #    @staticmethod
    #    def dict_merge(dct: Dict[Any, Any], merge_dct: Dict[Any, Any]) -> None:
    #        """Recursively merge merge_dct into dct, updating nested dictionaries.
    #
    #        Args:
    #            dct: The dictionary to update.
    #            merge_dct: The dictionary to merge into dct.
    #        """
    #        for key, value in merge_dct.items():
    #            if key in dct and isinstance(dct[key], dict) and isinstance(value, dict):
    #                Emulator.dict_merge(dct[key], value)
    #            else:
    #                dct[key] = value
    #

    @staticmethod
    def dict_merge(dest: SystemConfigDict, src: SystemConfigDict) -> None:
        """Merge src into dest, updating nested dictionaries.

        Args:
            dest: The dictionary to update.
            src: The dictionary to merge into dest.
        """
        stack = [(dest, src)]
        while stack:
            d, s = stack.pop()
            for k, v in s.items():
                if k in d and isinstance(d[k], dict) and isinstance(v, dict):
                    stack.append((d[k], v))
                else:
                    d[k] = v

    @staticmethod
    def get_generic_config(
        system: str, defaultyml: str, defaultarchyml: str
    ) -> dict[str, Any]:
        """Load and merge generic configuration from YAML files.

        Args:
            system (str): The system name (e.g., 'nes', 'snes').
            defaultyml (str): Path to the default YAML configuration file.
            defaultarchyml (str): Path to the architecture-specific YAML configuration file.

        Returns:
            Dict[str, Any]: Merged configuration dictionary.
        """
        # Load default configuration
        with open(defaultyml) as f:
            systems_default = yaml.load(f, Loader=Loader)

        # Load architecture-specific configuration if available
        systems_default_arch: dict[str, Any] = {}
        if path.exists(defaultarchyml):
            with open(defaultarchyml) as f:
                systems_default_arch = yaml.load(f, Loader=Loader) or {}

        dict_all: dict[str, Any] = {}

        # Merge default configurations
        if "default" in systems_default:
            dict_all = systems_default["default"]

        if "default" in systems_default_arch:
            Emulator.dict_merge(dict_all, systems_default_arch["default"])

        # Merge system-specific configurations
        if system in systems_default:
            Emulator.dict_merge(dict_all, systems_default[system])

        if system in systems_default_arch:
            Emulator.dict_merge(dict_all, systems_default_arch[system])  # type: ignore

        return dict_all

    @staticmethod
    def get_system_config(
        system: str, defaultyml: str, defaultarchyml: str
    ) -> SystemConfigDict:
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
        dict_result: SystemConfigDict = {
            "emulator": dict_all["emulator"],
            "core": dict_all["core"],
        }
        if "options" in dict_all:
            Emulator.dict_merge(dict_result, dict_all["options"])
        return dict_result

    def isOptSet(self, key: str) -> bool:
        """Check if a configuration option is set.

        Args:
            key: The configuration option key.

        Returns:
            True if the key exists in the config, False otherwise.
        """
        return key in self.config

    def getOptBoolean(self, key: str) -> bool:
        """Get a configuration option as a boolean value.

        Args:
            key: The configuration option key.

        Returns:
            True if the option is set to a truthy value, False otherwise.
        """
        true_values: set[str | bool] = {"1", "true", "on", "enabled", True}
        value = self.config.get(key)

        if isinstance(value, str):
            value = value.lower()

        return value in true_values

    def getOptString(self, key: str) -> str:
        """Get a configuration option as a string.

        Args:
            key: The configuration option key.

        Returns:
            The option value as a string, or empty string if not set.
        """
        return str(self.config.get(key, ""))

    @staticmethod
    def updateConfiguration(config: SystemConfigDict, settings: dict[str, Any]) -> None:
        """Update a configuration dictionary with new settings, ignoring invalid values.

        Args:
            config: The configuration dictionary to update.
            settings: The new settings to apply.
        """
        # Remove invalid settings ("default", "auto", or empty)
        # Using walrus operator to avoid re-evaluating settings[k]
        invalid_settings = [
            k for k, v in settings.items() if v in ("", "default", "auto")
        ]
        for k in invalid_settings:
            settings.pop(k, None)  # Safely remove without KeyError

        for key, value in settings.items():
            config[key] = value

    def updateFromESSettings(self) -> None:
        """Update emulator config with settings from EmulationStation XML file.

        Reads settings like showFPS and uimode from the EmulationStation configuration.
        Sets default values if the file is unavailable or parsing fails.
        """
        try:
            esConfig = ET.parse(ES_SETTINGS)

            # Read showFPS setting
            drawframerate_elem = esConfig.find("./bool[@name='DrawFramerate']")
            if drawframerate_elem is not None:
                drawframerate_value = drawframerate_elem.attrib.get("value", "false")
            else:
                drawframerate_value = "false"
            if drawframerate_value not in ["false", "true"]:
                drawframerate_value = "false"
            self.config["showFPS"] = drawframerate_value  # type: ignore

            # Read uimode setting
            uimode_elem = esConfig.find("./string[@name='UIMode']")
            if uimode_elem is not None:
                uimode_value = uimode_elem.attrib.get("value", "Full")
            else:
                uimode_value = "Full"
            if uimode_value not in ["Full", "Kiosk", "Kid"]:
                uimode_value = "Full"
            self.config["uimode"] = uimode_value  # type: ignore

        except ET.ParseError as e:
            eslog.warning(
                f"Failed to parse EmulationStation settings file {ES_SETTINGS}: {e}"
            )
            # Use defaults if ES settings cannot be loaded
            self.config["showFPS"] = "false"  # type: ignore
            self.config["uimode"] = "Full"  # type: ignore
        except FileNotFoundError:
            eslog.warning(f"EmulationStation settings file not found: {ES_SETTINGS}")
            # Use defaults if ES settings cannot be loaded
            self.config["showFPS"] = "false"  # type: ignore
            self.config["uimode"] = "Full"  # type: ignore
        except Exception as e:
            eslog.warning(f"Unexpected error reading EmulationStation settings: {e}")
            # Use defaults if ES settings cannot be loaded
            self.config["showFPS"] = "false"  # type: ignore
            self.config["uimode"] = "Full"  # type: ignore
