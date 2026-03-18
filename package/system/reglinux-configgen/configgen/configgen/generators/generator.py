from abc import ABC, abstractmethod
from typing import Any, Protocol

from configgen.core import Command, Emulator

# Type alias for device configurations (guns, wheels)
# Can be either a dict or list of dicts for backwards compatibility
DeviceConfig = dict[str, Any] | list[dict[str, Any]]


class GeneratorProtocol(Protocol):
    """Protocol defining the interface for emulator generators."""

    def generate(
        self,
        system: Emulator,
        rom: str,
        players_controllers: dict[str, Any],
        metadata: dict[str, Any],
        guns: DeviceConfig,
        wheels: DeviceConfig,
        game_resolution: dict[str, Any],
    ) -> Command:
        """Generate the command to launch the emulator with the specified configurations.

        Args:
            system: The Emulator instance with its configurations
            rom: Path to the ROM file to launch
            players_controllers: Controller configurations for players
            metadata: Game metadata
            guns: Light gun configurations
            wheels: Racing wheel configurations
            game_resolution: Game resolution settings

        Returns:
            Command object with the emulator command and environment settings

        """
        ...


class Generator(ABC):
    @abstractmethod
    def generate(
        self,
        system: Emulator,
        rom: str,
        players_controllers: dict[str, Any],
        metadata: dict[str, Any],
        guns: DeviceConfig,
        wheels: DeviceConfig,
        game_resolution: dict[str, Any],
    ) -> Command:
        """Retrieve the command to start the emulator with the specified configurations."""
        return Command(array=[])

    def getResolutionMode(self, config: dict[str, Any]) -> str:
        """Get the video mode from config."""
        return config["videomode"]

    def getMouseMode(self, config: dict[str, Any], rom: str) -> bool:
        """Check if mouse should be visible."""
        return False

    def executionDirectory(self, config: dict[str, Any], rom: str) -> str:
        """Get the execution directory for the emulator."""
        return None  # type: ignore

    # mame or libretro have internal bezels, don't display the one of mangohud
    def supportsInternalBezels(self) -> bool:
        """Check if emulator has internal bezel support."""
        return False

    # mangohud must be called by the generator itself
    def hasInternalMangoHUDCall(self) -> bool:
        """Check if emulator has internal MangoHUD support."""
        return False

    def getInGameRatio(
        self,
        config: dict[str, Any],
        gameResolution: dict[str, Any],
        rom: str,
    ) -> float:
        """Get the in-game aspect ratio."""
        # put a default value, but it should be overriden by generators
        return 4 / 3

    # this emulator/core requires wayland compositor to run
    def requiresWayland(self) -> bool:
        """Check if emulator requires Wayland."""
        return False

    # this emulator/core requires a X server to run
    def requiresX11(self) -> bool:
        """Check if emulator requires X11."""
        return False
