from pathlib import Path

from configgen.Command import Command
from configgen.controllers import generate_sdl_controller_config
from configgen.generators.Generator import Generator
from configgen.settings import JSONSettings

from .ikemenControllers import Joymapping, Keymapping

IKEMEN_CONFIG_PATH = Path("/save/config.json")
IKEMEN_BIN_PATH = Path("/usr/bin/system-ikemen")


class IkemenGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        # Convert rom to Path if it's not already
        rom_path = Path(rom) if not isinstance(rom, Path) else rom

        # Load existing config or create a new one
        config_path = rom_path / IKEMEN_CONFIG_PATH
        ikemenConfig = JSONSettings(str(config_path))

        # Joystick configuration seems completely broken in 0.98.2 Linux
        # so let's force keyboad and use a pad2key
        ikemenConfig["KeyConfig"] = Keymapping
        ikemenConfig["JoystickConfig"] = Joymapping
        ikemenConfig["Fullscreen"] = True

        # Save the updated configuration
        ikemenConfig.write()

        command_array = [str(IKEMEN_BIN_PATH), str(rom_path)]

        return Command(
            array=command_array,
            env={
                "SDL_GAMECONTROLLERCONFIG": generate_sdl_controller_config(
                    players_controllers
                )
            },
        )
