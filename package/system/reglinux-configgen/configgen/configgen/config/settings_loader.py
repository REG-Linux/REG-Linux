"""Settings loader for REG-Linux ConfigGen.

This module provides a unified interface for loading settings from various
configuration sources with proper precedence.
"""

from pathlib import Path
from typing import Any

from configgen.config.paths import SYSTEM_CONF
from configgen.settings import UnixSettings


class SettingsLoader:
    """Loads settings from various configuration sources.

    This class handles loading settings from system.conf with proper precedence:
    1. Controllers settings
    2. Global settings
    3. System-specific settings
    4. Folder-specific settings
    5. Game-specific settings
    """

    def __init__(self, system_conf_path: Path = SYSTEM_CONF):
        """Initialize the settings loader.

        Args:
            system_conf_path: Path to the system.conf file.

        """
        self.settings = UnixSettings(system_conf_path)

    def load_controllers(self, with_index: bool = False) -> dict[str, Any]:
        """Load controller settings.

        Args:
            with_index: Whether to include index in the settings.

        Returns:
            Dictionary of controller settings.

        """
        return self.settings.loadAll("controllers", with_index)

    def load_global(self) -> dict[str, Any]:
        """Load global settings.

        Returns:
            Dictionary of global settings.

        """
        return self.settings.loadAll("global")

    def load_system(self, system: str) -> dict[str, Any]:
        """Load system-specific settings.

        Args:
            system: The system name (e.g., 'nes', 'snes').

        Returns:
            Dictionary of system settings.

        """
        return self.settings.loadAll(system)

    def load_folder(self, system: str, rom: str) -> dict[str, Any]:
        """Load folder-specific settings.

        Args:
            system: The system name.
            rom: Path to the ROM file.

        Returns:
            Dictionary of folder settings.

        """
        folder_path = str(Path(rom).parent)
        return self.settings.loadAll(f'{system}.folder["{folder_path}"]')

    def load_game(self, system: str, rom: str) -> dict[str, Any]:
        """Load game-specific settings.

        Args:
            system: The system name.
            rom: Path to the ROM file.

        Returns:
            Dictionary of game settings.

        """
        from configgen.core.emulator import Emulator

        gsname = Emulator.game_settings_name(rom)
        return self.settings.loadAll(f'{system}["{gsname}"]')

    def load_display(self) -> dict[str, Any]:
        """Load display settings.

        Returns:
            Dictionary of display settings.

        """
        return self.settings.loadAll("display")

    def load_renderer(self, system: str, rom: str | None = None) -> dict[str, Any]:
        """Load renderer-specific settings.

        Args:
            system: The system name.
            rom: Optional ROM path for game-specific renderer settings.

        Returns:
            Dictionary of renderer settings.

        """
        result: dict[str, Any] = {}

        # Load system renderer settings
        system_settings = self.settings.loadAll(f"{system}-renderer")
        result.update(system_settings)

        # Load game renderer settings if ROM is provided
        if rom:
            gsname = Path(rom).name
            game_settings = self.settings.loadAll(f'{system}["{gsname}"]-renderer')
            result.update(game_settings)

        return result

    def load_merged(self, system: str, rom: str) -> dict[str, Any]:
        """Load all settings with proper precedence.

        Settings are merged in the following order (later overrides earlier):
        1. Controllers settings
        2. Global settings
        3. System-specific settings
        4. Folder-specific settings
        5. Game-specific settings

        Args:
            system: The system name.
            rom: Path to the ROM file.

        Returns:
            Merged dictionary of all settings.

        """
        config: dict[str, Any] = {}

        # Load display settings first
        display_settings = self.load_display()
        for opt in display_settings:
            config[f"display.{opt}"] = display_settings[opt]

        # Load and merge settings in order of precedence
        self._merge_config(config, self.load_controllers(True))
        self._merge_config(config, self.load_global())
        self._merge_config(config, self.load_system(system))
        self._merge_config(config, self.load_folder(system, rom))
        self._merge_config(config, self.load_game(system, rom))

        return config

    @staticmethod
    def _merge_config(config: dict[str, Any], settings: dict[str, Any]) -> None:
        """Merge settings into config, removing invalid values.

        Args:
            config: The configuration dictionary to update.
            settings: The settings to merge.

        """
        # Remove invalid settings ("default", "auto", or empty)
        invalid_settings = [
            k for k, v in settings.items() if v in ("", "default", "auto")
        ]
        for k in invalid_settings:
            settings.pop(k, None)

        config.update(settings)
