from abc import ABCMeta, abstractmethod
from configgen.Command import Command


class Generator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution) -> Command:
        pass

    def getResolutionMode(self, config) -> str:
        return config['videomode']

    def getMouseMode(self, config, rom) -> bool:
        return False

    def executionDirectory(self, config, rom):
        return None

    # mame or libretro have internal bezels, don't display the one of mangohud
    def supportsInternalBezels(self) -> bool:
        return False

    # mangohud must be called by the generator itself
    def hasInternalMangoHUDCall(self) -> bool:
        return False

    def getInGameRatio(self, config, gameResolution, rom):
        # put a default value, but it should be overriden by generators
        return 4/3

    # this emulator/core requires wayland compositor to run
    def requiresWayland(self) -> bool:
        return False

    # this emulator/core requires a X server to run
    def requiresX11(self) -> bool:
        return False
