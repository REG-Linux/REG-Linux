"""Emulator domain model for REG-Linux ConfigGen.

This module contains the Emulator class which represents the domain model
for emulator configurations.
"""

from pathlib import Path
from typing import Any, TypedDict

from configgen.config.paths import ES_SETTINGS, SYSTEM_CONF
from configgen.core.emulator_config import load_emulator_config, load_render_config
from configgen.core.exceptions import EmulatorNotFoundError
from configgen.settings import UnixSettings
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


# Defining TypedDicts for configuration structures
class SystemConfigRequired(TypedDict, total=True):
    """Required fields in SystemConfig."""

    emulator: str
    core: str


class SystemConfigOptional(TypedDict, total=False):
    """Optional fields in SystemConfig."""

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
    # Shader settings (dynamically added from config)
    shaderset: str


class SystemConfig(SystemConfigRequired, SystemConfigOptional):
    """System configuration with required and optional fields."""


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
# Using dict[str, Any] to allow dynamic keys while maintaining type safety
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

        # Load system configuration
        self.config = load_emulator_config(name, rom)

        if "emulator" not in self.config or self.config["emulator"] == "":
            eslog.error("No emulator defined. Exiting.")
            raise EmulatorNotFoundError(name)

        # Load settings from system.conf
        self._load_system_settings(rom)

        # Check if emulator or core is forcibly set
        self._check_forced_settings()

        # Load render configuration
        self.renderconfig = load_render_config(name, self.config)

    def _load_system_settings(self, rom: str) -> None:
        """Load settings from system.conf with proper precedence."""
        recalSettings = UnixSettings(SYSTEM_CONF)

        # Get sanitized game settings name from ROM
        gsname = self.game_settings_name(rom)

        # Load all setting levels
        controllersSettings = recalSettings.loadAll("controllers", True)
        globalSettings = recalSettings.loadAll("global")
        systemSettings = recalSettings.loadAll(self.name)
        folderSettings = recalSettings.loadAll(
            self.name + '.folder["' + str(Path(rom).parent) + '"]',
        )
        gameSettings = recalSettings.loadAll(self.name + '["' + gsname + '"]')

        # Add display settings
        displaySettings = recalSettings.loadAll("display")
        for opt in displaySettings:
            self.config["display." + opt] = displaySettings[opt]

        # Update config with settings in order of precedence
        Emulator.updateConfiguration(self.config, controllersSettings)
        Emulator.updateConfiguration(self.config, globalSettings)
        Emulator.updateConfiguration(self.config, systemSettings)
        Emulator.updateConfiguration(self.config, folderSettings)
        Emulator.updateConfiguration(self.config, gameSettings)

        # Update from EmulationStation settings
        self.updateFromESSettings()
        eslog.debug(f"uimode: {self.config.get('uimode')}")

    def _check_forced_settings(self) -> None:
        """Check if emulator or core settings are forced."""
        recalSettings = UnixSettings(SYSTEM_CONF)
        gsname = self.game_settings_name(self.rom)

        globalSettings = recalSettings.loadAll("global")
        systemSettings = recalSettings.loadAll(self.name)
        gameSettings = recalSettings.loadAll(self.name + '["' + gsname + '"]')

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

    @staticmethod
    def game_settings_name(rom: str) -> str:
        """Generate a sanitized game settings name from the ROM file name.

        Args:
            rom: Path to the ROM file.

        Returns:
            Sanitized game settings name compatible with EmulationStation.

        """
        from pathlib import Path

        rom = Path(rom).name

        # Sanitize name by removing invalid characters per EmulationStation rules
        if "=" in rom or "#" in rom:
            rom = rom.replace("=", "").replace("#", "")

        eslog.info(f"game settings name: {rom}")
        return rom

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
    def updateConfiguration(config: SystemConfigDict, settings: dict[str, Any]) -> None:
        """Update a configuration dictionary with new settings, ignoring invalid values.

        Args:
            config: The configuration dictionary to update.
            settings: The new settings to apply.

        """
        # Filter and update in a single pass
        INVALID_VALUES = frozenset(("", "default", "auto"))
        for key, value in settings.items():
            if value not in INVALID_VALUES:
                config[key] = value

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

    def updateFromESSettings(self) -> None:
        """Update emulator config with settings from EmulationStation XML file.

        Reads settings like showFPS and uimode from the EmulationStation configuration.
        Sets default values if the file is unavailable or parsing fails.
        """
        import xml.etree.ElementTree as ET

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
            self.config["showFPS"] = drawframerate_value

            # Read uimode setting
            uimode_elem = esConfig.find("./string[@name='UIMode']")
            if uimode_elem is not None:
                uimode_value = uimode_elem.attrib.get("value", "Full")
            else:
                uimode_value = "Full"
            if uimode_value not in ["Full", "Kiosk", "Kid"]:
                uimode_value = "Full"
            self.config["uimode"] = uimode_value

        except ET.ParseError as e:
            eslog.warning(
                f"Failed to parse EmulationStation settings file {ES_SETTINGS}: {e}",
            )
            # Use defaults if ES settings cannot be loaded
            self.config["showFPS"] = "false"
            self.config["uimode"] = "Full"
        except FileNotFoundError:
            eslog.warning(f"EmulationStation settings file not found: {ES_SETTINGS}")
            # Use defaults if ES settings cannot be loaded
            self.config["showFPS"] = "false"
            self.config["uimode"] = "Full"
        except Exception as e:
            eslog.warning(f"Unexpected error reading EmulationStation settings: {e}")
            # Use defaults if ES settings cannot be loaded
            self.config["showFPS"] = "false"
            self.config["uimode"] = "Full"
