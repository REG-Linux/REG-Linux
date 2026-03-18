from pathlib import Path

from configgen.config.paths import CONF
from configgen.core import Command
from configgen.generators.generator import Generator
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

DOSBOXSTAGING_CONFIG_DIR = str(Path(CONF) / "dosbox")
DOSBOXSTAGING_CONFIG_PATH = str(Path(DOSBOXSTAGING_CONFIG_DIR) / "dosbox.conf")
DOSBOXSTAGING_BIN_PATH = "/usr/bin/dosbox-staging"


class DosBoxStagingGenerator(Generator):
    def generate(
        self,
        system,
        rom,
        players_controllers,
        metadata,
        guns,
        wheels,
        game_resolution,
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
        ]

        # Add dosbox.bat if it exists, otherwise mount and run
        if Path(batFile).is_file():
            command_array.append(batFile)
        else:
            command_array.extend([
                "-c",
                f"mount c {gameDir}",
                "-c",
                "c:",
                "-c",
                "dir /b *.bat | findstr /i dosbox > temp.txt",
                "-c",
                "set /p batfile=<temp.txt",
                "-c",
                "if exist %batfile% call %batfile% else echo No batch file found",
            ])

        command_array.extend([
            "-c",
            f"set ROOT={gameDir}",
        ])

        if Path(gameConfFile).is_file():
            command_array.append("-conf")
            command_array.append(gameConfFile)
        else:
            command_array.append("-conf")
            command_array.append(DOSBOXSTAGING_CONFIG_PATH)

        return Command(array=command_array)
