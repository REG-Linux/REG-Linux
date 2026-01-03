from pathlib import Path

from configgen.Command import Command
from configgen.generators.Generator import Generator
from configgen.systemFiles import CONF
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

DOSBOXSTAGING_CONFIG_DIR = str(Path(CONF) / "dosbox")
DOSBOXSTAGING_CONFIG_PATH = str(Path(DOSBOXSTAGING_CONFIG_DIR) / "dosbox.conf")
DOSBOXSTAGING_BIN_PATH = "/usr/bin/dosbox-staging"


class DosBoxStagingGenerator(Generator):
    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution,
    ):
        # Find rom path
        gameDir = rom
        batFile = str(Path(gameDir) / "dosbox.bat")
        gameConfFile = str(Path(gameDir) / "dosbox.cfg")

        command_array = [
            DOSBOXSTAGING_BIN_PATH,
            "-fullscreen",
            "-userconf",
            "-exit",
            f"""{batFile}""",
            "-c",
            f"""set ROOT={gameDir}""",
        ]
        if Path(gameConfFile).is_file():
            command_array.append("-conf")
            command_array.append(f"""{gameConfFile}""")
        else:
            command_array.append("-conf")
            command_array.append(f"""{DOSBOXSTAGING_CONFIG_PATH}""")

        return Command(array=command_array)
