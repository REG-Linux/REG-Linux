from configgen.generators.Generator import Generator
from configgen.Command import Command
from shutil import copy
from os import path, remove, makedirs
from re import search, MULTILINE
from configgen.controllers import write_sdl_db_all_controllers
from .pcsx2Controllers import isPlayingWithWheel
from .pcsx2Config import (
    setPcsx2Reg,
    setPcsx2Config,
    configureAudio,
    PCSX2_CONFIG_DIR,
    PCSX2_SOURCE_PATH,
    PCSX2_BIN_PATH,
    PCSX2_PATCHES_PATH,
    PCSX2_BIOS_DIR,
)

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


class Pcsx2Generator(Generator):
    # PCSX2 requires wayland compositor to run
    # TODO check if it works without X (it should)
    def requiresWayland(self):
        return True

    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        # Remove older config files if present
        inisDir = path.join(PCSX2_CONFIG_DIR, "inis")
        files_to_remove = ["PCSX2_ui.ini", "PCSX2_vm.ini", "GS.ini"]
        for filename in files_to_remove:
            file_path = path.join(inisDir, filename)
            if path.exists(file_path):
                remove(file_path)

        # FIXME Implement logic to determine if playing with wheel
        playingWithWheel = isPlayingWithWheel(system, wheels)

        # FIXME Config files
        setPcsx2Reg()
        setPcsx2Config(
            system, rom, playersControllers, metadata, guns, wheels, playingWithWheel
        )
        configureAudio()

        # write our own game_controller_db.txt file before launching the game
        dbfile = PCSX2_CONFIG_DIR + "/game_controller_db.txt"
        write_sdl_db_all_controllers(playersControllers, dbfile)

        commandArray = (
            [PCSX2_BIN_PATH] if rom == "config" else [PCSX2_BIN_PATH, "-nogui", rom]
        )

        with open("/proc/cpuinfo") as cpuinfo:
            if not search(r"^flags\s*:.*\ssse4_1\W", cpuinfo.read(), MULTILINE):
                eslog.warning(
                    "CPU does not support SSE4.1 which is required by pcsx2.  The emulator will likely crash with SIGILL (illegal instruction)."
                )

        # ensure we have the patches.zip file to avoid message.
        if not path.exists(PCSX2_BIOS_DIR):
            makedirs(PCSX2_BIOS_DIR)
        if not path.exists(PCSX2_PATCHES_PATH):
            copy(PCSX2_SOURCE_PATH, PCSX2_PATCHES_PATH)

        return Command(array=commandArray)
