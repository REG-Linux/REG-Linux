from abc import ABCMeta, abstractmethod
from typing import Protocol, Dict, Any, List
from configgen.Command import Command
from configgen.Emulator import Emulator


class GeneratorProtocol(Protocol):
    """Protocol defining the interface for emulator generators."""

    def generate(self, system: Emulator, rom: str, playersControllers: Dict[str, Any], metadata: Dict[str, Any], guns: List[Any], wheels: List[Any], gameResolution: Dict[str, Any]) -> Command:
        """Generate the command to launch the emulator with the specified configurations.

        Args:
            system: The Emulator instance with its configurations
            rom: Path to the ROM file to launch
            playersControllers: Controller configurations for players
            metadata: Game metadata
            guns: Light gun configurations
            wheels: Racing wheel configurations
            gameResolution: Game resolution settings

        Returns:
            Command object with the emulator command and environment settings
        """
        ...


class Generator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def generate(
        self, system: Emulator, rom: str, playersControllers: Dict[str, Any], metadata: Dict[str, Any], guns: List[Any], wheels: List[Any], gameResolution: Dict[str, Any]
    ) -> Command:
        """
        Retrieve the command to start the emulator with the specified configurations.
        """
        return Command(array=[])

    def getResolutionMode(self, config: Dict[str, Any]) -> str:
        return config["videomode"]

    def getMouseMode(self, config: Dict[str, Any], rom: str) -> bool:
        return False

    def executionDirectory(self, config: Dict[str, Any], rom: str) -> str:
        return None  # type: ignore

    # mame or libretro have internal bezels, don't display the one of mangohud
    def supportsInternalBezels(self) -> bool:
        return False

    # mangohud must be called by the generator itself
    def hasInternalMangoHUDCall(self) -> bool:
        return False

    def getInGameRatio(self, config: Dict[str, Any], gameResolution: Dict[str, Any], rom: str) -> float:
        # put a default value, but it should be overriden by generators
        return 4 / 3

    # this emulator/core requires wayland compositor to run
    def requiresWayland(self) -> bool:
        return False

    # this emulator/core requires a X server to run
    def requiresX11(self) -> bool:
        return False
