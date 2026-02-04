from pathlib import Path
from re import MULTILINE, search
from shutil import copy
from typing import Any

from configgen.command import Command
from configgen.controllers import write_sdl_db_all_controllers
from configgen.generators.generator import Generator
from configgen.utils.logger import get_logger

from .pcsx2Config import (
    PCSX2_BIN_PATH,
    PCSX2_BIOS_DIR,
    PCSX2_CONFIG_DIR,
    PCSX2_PATCHES_PATH,
    PCSX2_SOURCE_PATH,
    configureAudio,
    getInGameRatio,
    setPcsx2Config,
    setPcsx2Reg,
)
from .pcsx2Controllers import isPlayingWithWheel

eslog = get_logger(__name__)


class Pcsx2Generator(Generator):
    # PCSX2 requires wayland compositor to run
    # TODO check if it works without X (it should)
    def requiresWayland(self):
        return True

    def getInGameRatio(
        self,
        config: dict[str, Any],
        gameResolution: dict[str, Any],
        rom: str,
    ) -> float:
        """Calculate the in-game aspect ratio for PCSX2 based on configuration.

        Args:
            config: Configuration dictionary containing settings
            gameResolution: Dictionary containing game resolution (width, height)
            rom: Path to the ROM file being loaded

        Returns:
            float: The calculated aspect ratio as a fraction (e.g., 4/3, 16/9)

        """
        return getInGameRatio(config, gameResolution, rom)

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
        # Remove older config files if present
        inisDir = Path(PCSX2_CONFIG_DIR) / "inis"
        files_to_remove = ["PCSX2_ui.ini", "PCSX2_vm.ini", "GS.ini"]
        for filename in files_to_remove:
            file_path = inisDir / filename
            if file_path.exists():
                file_path.unlink()

        # FIXME Implement logic to determine if playing with wheel
        playingWithWheel = isPlayingWithWheel(system, wheels)

        # FIXME Config files
        setPcsx2Reg()
        setPcsx2Config(
            system,
            rom,
            players_controllers,
            metadata,
            guns,
            wheels,
            playingWithWheel,
        )
        configureAudio()

        # write our own game_controller_db.txt file before launching the game
        dbfile = str(Path(PCSX2_CONFIG_DIR) / "game_controller_db.txt")
        write_sdl_db_all_controllers(players_controllers, dbfile)

        command_array = (
            [str(PCSX2_BIN_PATH)]
            if rom == "config"
            else [str(PCSX2_BIN_PATH), "-nogui", str(rom)]
        )

        with Path("/proc/cpuinfo").open() as cpuinfo:
            if not search(r"^flags\s*:.*\ssse4_1\W", cpuinfo.read(), MULTILINE):
                eslog.warning(
                    "CPU does not support SSE4.1 which is required by pcsx2.  The emulator will likely crash with SIGILL (illegal instruction).",
                )

        # ensure we have the patches.zip file to avoid message.
        bios_dir_path = Path(PCSX2_BIOS_DIR)
        if not bios_dir_path.exists():
            bios_dir_path.mkdir(parents=True, exist_ok=True)
        patches_path = Path(PCSX2_PATCHES_PATH)
        if not patches_path.exists():
            copy(PCSX2_SOURCE_PATH, PCSX2_PATCHES_PATH)

        return Command(array=command_array)
