from generators.Generator import Generator
from Command import Command
from os import path, makedirs, chdir
from re import search
from systemFiles import CONF, SAVES, ROMS
from settings import UnixSettings
from .openborControllers import setControllerConfig

OPENBOR_CONF_DIR = CONF + "/openbor"
OPENBOR_SAVES_DIR = SAVES + "/openbor"
OPENBOR_ROMS_DIR = ROMS + "/openbor"


class OpenborGenerator(Generator):
    # Main entry of the module
    def generate(
        self, system, rom, playersControllers, metadata, guns, wheels, gameResolution
    ):
        if not path.exists(OPENBOR_CONF_DIR):
            makedirs(OPENBOR_CONF_DIR)

        if not path.exists(OPENBOR_SAVES_DIR):
            makedirs(OPENBOR_SAVES_DIR)

        # guess the version to run
        core = system.config["core"]
        if system.config["core_forced"] == False:
            core = OpenborGenerator.guessCore(rom)

        # config file
        configfilename = "config7530.ini"
        if core == "openbor4432":
            configfilename = "config4432.ini"
        elif core == "openbor6412":
            configfilename = "config6412.ini"
        elif core == "openbor7142":
            configfilename = "config7142.ini"
        elif core == "openbor7530":
            configfilename = "config7530.ini"

        config = UnixSettings(OPENBOR_CONF_DIR + "/" + configfilename, separator="")

        # general
        config.save("fullscreen", "1")
        config.save("usegl", "1")
        config.save("usejoy", "1")

        # options
        if system.isOptSet("openbor_ratio"):
            config.save("stretch", system.config["openbor_ratio"])
        else:
            config.save("stretch", "0")

        if system.isOptSet("openbor_filter"):
            config.save("swfilter", system.config["openbor_filter"])
        else:
            config.save("swfilter", "0")

        if system.isOptSet("openbor_vsync"):
            config.save("vsync", system.config["openbor_vsync"])
        else:
            config.save("vsync", "1")

        if system.isOptSet("openbor_limit"):
            config.save("fpslimit", system.config["openbor_limit"])
        else:
            config.save("fpslimit", "0")

        # controllers
        setControllerConfig(config, playersControllers, core)

        # rumble
        if system.isOptSet("openbor_rumble"):
            config.save("joyrumble.0", system.config["openbor_rumble"])
            config.save("joyrumble.1", system.config["openbor_rumble"])
            config.save("joyrumble.2", system.config["openbor_rumble"])
            config.save("joyrumble.3", system.config["openbor_rumble"])
        else:
            config.save("joyrumble.0", "0")
            config.save("joyrumble.1", "0")
            config.save("joyrumble.2", "0")
            config.save("joyrumble.3", "0")

        config.write()

        # change directory for wider compatibility
        chdir(OPENBOR_ROMS_DIR)

        return OpenborGenerator.executeCore(core, rom)

    @staticmethod
    def executeCore(core, rom):
        if core == "openbor4432":
            commandArray = ["OpenBOR4432", rom]
        elif core == "openbor6412":
            commandArray = ["OpenBOR6412", rom]
        elif core == "openbor7142":
            commandArray = ["OpenBOR7142", rom]
        elif core == "openbor7530":
            commandArray = ["OpenBOR7530", rom]
        else:
            commandArray = ["OpenBOR7530", rom]
        return Command(array=commandArray)

    @staticmethod
    def guessCore(rom):
        versionstr = search(r"\[.*([0-9]{4})\]+", path.basename(rom))
        if versionstr == None:
            return "openbor7530"
        version = int(versionstr.group(1))

        if version < 6000:
            return "openbor4432"
        if version < 6500:
            return "openbor6412"
        if version < 7530:
            return "openbor7142"
        return "openbor7530"
