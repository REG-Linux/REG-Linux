from configparser import ConfigParser
from os import makedirs, path

from configgen.Command import Command
from configgen.generators.Generator import Generator
from configgen.utils.logger import get_logger

from .duckstationConfig import (
    DUCKSTATION_BIN_PATH,
    DUCKSTATION_CONFIG_PATH,
    DUCKSTATION_NOGUI_PATH,
    setDuckstationConfig,
)
from .duckstationControllers import setDuckstationControllers

eslog = get_logger(__name__)


class DuckstationGenerator(Generator):
    # Duckstation is now QT-only, requires wayland compositor to run
    def requiresWayland(self):
        return True

    def generate(
        self, system, rom, players_controllers, metadata, guns, wheels, game_resolution
    ):
        duckstatonConfig = ConfigParser(interpolation=None)
        duckstatonConfig.optionxform = lambda optionstr: str(optionstr)

        if path.exists(DUCKSTATION_CONFIG_PATH):
            duckstatonConfig.read(DUCKSTATION_CONFIG_PATH)

        setDuckstationConfig(duckstatonConfig, system, players_controllers)
        setDuckstationControllers(
            duckstatonConfig, system, metadata, guns, players_controllers
        )

        # Save config
        if not path.exists(path.dirname(DUCKSTATION_CONFIG_PATH)):
            makedirs(path.dirname(DUCKSTATION_CONFIG_PATH))
        with open(DUCKSTATION_CONFIG_PATH, "w") as configfile:
            duckstatonConfig.write(configfile)

        # Test if it's a m3u file
        if path.splitext(rom)[1] == ".m3u":
            rom = rewriteM3uFullPath(rom)

        if path.exists(DUCKSTATION_BIN_PATH):
            command_array = [DUCKSTATION_BIN_PATH, rom]
        else:
            command_array = [DUCKSTATION_NOGUI_PATH, "-batch", "-fullscreen", "--", rom]

        return Command(array=command_array)


def rewriteM3uFullPath(m3u: str) -> str:  # Rewrite a clean m3u file with valid fullpath
    # get initialm3u
    try:
        with open(m3u) as f:
            firstline = f.readline().rstrip()  # Get first line in m3u
    except OSError as e:
        eslog.error(f"Error reading m3u file {m3u}: {e}")
        # Return the original m3u in case of error
        return m3u

    initialfirstdisc = (
        "/tmp/" + path.splitext(path.basename(firstline))[0] + ".m3u"
    )  # Generating a temp path with the first iso filename in m3u

    # create a temp m3u to bypass Duckstation m3u bad pathfile
    fulldirname = path.dirname(m3u)

    try:
        with open(m3u) as initialm3u, open(initialfirstdisc, "a") as f1:
            for line in initialm3u:
                if line[0] == "/":  # for /MGScd1.chd
                    newpath = fulldirname + line
                else:
                    newpath = fulldirname + "/" + line  # for MGScd1.chd
                f1.write(newpath)
    except OSError as e:
        eslog.error(f"Error rewriting m3u file {m3u}: {e}")
        # Return the original m3u in case of error
        return m3u

    return initialfirstdisc
