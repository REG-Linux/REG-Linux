from configgen.generators.Generator import Generator
from configgen.Command import Command
from os import path
from .hatariControllers import setHatariControllers
from .hatariConfig import HATARI_BIOS_PATH, HATARI_BIN_PATH

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


class HatariGenerator(Generator):
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
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
        commandArray = [HATARI_BIN_PATH, "--fullscreen"]

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

        commandArray += ["--machine", machine]
        tos = HatariGenerator.findBestTos(
            HATARI_BIOS_PATH, machine, tosversion, toslang
        )
        commandArray += ["--tos", f"{HATARI_BIOS_PATH}/{tos}"]

        # RAM (ST Ram) options (0 for 512k, 1 for 1MB)
        memorysize = 0
        if system.isOptSet("ram"):
            memorysize = system.config["ram"]
        commandArray += ["--memsize", str(memorysize)]

        rom_extension = path.splitext(rom)[1].lower()
        if rom_extension == ".hd":
            if (
                system.isOptSet("hatari_drive")
                and system.config["hatari_drive"] == "ASCI"
            ):
                commandArray += ["--asci", rom]
            else:
                commandArray += ["--ide-master", rom]
        elif rom_extension == ".gemdos":
            blank_file = "/userdata/system/configs/hatari/blank.st"
            if not path.exists(blank_file):
                with open(blank_file, "w"):
                    pass
            commandArray += ["--harddrive", rom, blank_file]
        else:
            # Floppy (A) options
            commandArray += ["--disk-a", rom]
            # Floppy (B) options
            commandArray += ["--drive-b", "off"]

        # config file
        setHatariControllers(system, playersControllers)

        return Command(array=commandArray)

    @staticmethod
    def findBestTos(biosdir, machine, tos_version, language):
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
                    if path.exists(f"{biosdir}/{filename}"):
                        eslog.debug(f"tos filename: {filename}")
                        return filename
                    else:
                        eslog.warning(f"tos filename {filename} not found")

        raise Exception(f"no bios found for machine {machine}")
