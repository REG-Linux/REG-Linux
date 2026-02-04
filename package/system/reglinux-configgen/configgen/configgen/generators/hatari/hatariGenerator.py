from pathlib import Path

from configgen.command import Command
from configgen.generators.generator import Generator
from configgen.utils.logger import get_logger

from .hatariConfig import HATARI_BIN_PATH, HATARI_BIOS_PATH
from .hatariControllers import setHatariControllers

eslog = get_logger(__name__)


class HatariGenerator(Generator):
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
        model_mapping = {
            "520st_auto": {"machine": "st", "tos": "auto"},
            "520st_100": {"machine": "st", "tos": "100"},
            "520st_102": {"machine": "st", "tos": "102"},
            "520st_104": {"machine": "st", "tos": "104"},
            "1040ste_auto": {"machine": "ste", "tos": "auto"},
            "1040ste_106": {"machine": "ste", "tos": "106"},
            "1040ste_162": {"machine": "ste", "tos": "162"},
            "megaste_auto": {"machine": "megaste", "tos": "auto"},
            "megaste_205": {"machine": "megaste", "tos": "205"},
            "megaste_206": {"machine": "megaste", "tos": "206"},
        }

        # Start emulator fullscreen
        command_array = [HATARI_BIN_PATH, "--fullscreen"]

        # Machine can be st (default), ste, megaste, tt, falcon
        # st should use TOS 1.00 to TOS 1.04 (tos100 / tos102 / tos104)
        # ste should use TOS 1.06 at least (tos106 / tos162 / tos206)
        # megaste should use TOS 2.XX series (tos206)
        # tt should use tos 3.XX
        # falcon should use tos 4.XX

        machine = "st"
        tosversion = "auto"
        if system.isOptSet("model") and system.config["model"] in model_mapping:
            machine = model_mapping[system.config["model"]]["machine"]
            tosversion = model_mapping[system.config["model"]]["tos"]
        toslang = "us"
        if system.isOptSet("language"):
            toslang = system.config["language"]

        command_array += ["--machine", machine]
        tos = HatariGenerator.findBestTos(
            str(HATARI_BIOS_PATH),
            machine,
            tosversion,
            toslang,
        )
        command_array += ["--tos", f"{HATARI_BIOS_PATH!s}/{tos}"]

        # RAM (ST Ram) options (0 for 512k, 1 for 1MB)
        memorysize = 0
        if system.isOptSet("ram"):
            memorysize = system.config["ram"]
        command_array += ["--memsize", str(memorysize)]

        rom_extension = Path(rom).suffix.lower()
        if rom_extension == ".hd":
            if (
                system.isOptSet("hatari_drive")
                and system.config["hatari_drive"] == "ASCI"
            ):
                command_array += ["--asci", rom]
            else:
                command_array += ["--ide-master", rom]
        elif rom_extension == ".gemdos":
            blank_file = "/userdata/system/configs/hatari/blank.st"
            blank_path = Path(blank_file)
            if not blank_path.exists():
                with Path(blank_file).open("w"):
                    pass
            command_array += ["--harddrive", rom, blank_file]
        else:
            # Floppy (A) options
            command_array += ["--disk-a", rom]
            # Floppy (B) options
            command_array += ["--drive-b", "off"]

        # config file
        setHatariControllers(system, players_controllers)

        return Command(array=command_array)

    @staticmethod
    def findBestTos(biosdir: str, machine: str, tos_version: str, language: str) -> str:
        # all languages by preference, when value is "auto"
        all_languages = ["us", "uk", "de", "es", "fr", "it", "nl", "ru", "se", ""]

        # machine bioses by prefered orders, when value is "auto"
        all_machines_bios = {
            "st": ["104", "102", "100"],
            "ste": ["162", "106"],
            "megaste": ["206", "205"],
        }

        if machine in all_machines_bios:
            l_tos = []
            if tos_version != "auto":
                l_tos = [tos_version]
            l_tos.extend(all_machines_bios[machine])
            for v_tos_version in l_tos:
                l_lang = []
                if l_lang != "auto":
                    l_lang = [language]
                l_lang.extend(all_languages)
                for v_language in l_lang:
                    filename = f"tos{v_tos_version}{v_language}.img"
                    bios_path = Path(biosdir) / filename
                    if bios_path.exists():
                        eslog.debug(f"tos filename: {filename}")
                        return filename
                    eslog.warning(f"tos filename {filename} not found")

        raise Exception(f"no bios found for machine {machine}")
