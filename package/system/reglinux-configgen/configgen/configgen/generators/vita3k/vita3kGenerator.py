from generators.Generator import Generator
from Command import Command
from os import path, mkdir, listdir
from ruamel.yaml import YAML
from shutil import move
from controllers import generate_sdl_controller_config
from systemFiles import CONF, SAVES

VITA3K_CONFIG_DIR = CONF + '/vita3k'
VITA3K_SAVES_DIR = SAVES + '/psvita'
VITA3K_CONFIG_PATH = VITA3K_CONFIG_DIR + '/config.yml'
VITA3K_BIN_PATH = '/usr/bin/vita3k/Vita3K'

class Vita3kGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):
            # Create folder
            if not path.isdir(VITA3K_CONFIG_DIR):
                mkdir(VITA3K_CONFIG_DIR)
            if not path.isdir(VITA3K_SAVES_DIR):
                mkdir(VITA3K_SAVES_DIR)

            # Move saves if necessary
            if path.isdir(path.join(VITA3K_CONFIG_DIR, 'ux0')):
                # Move all folders from VITA3K_CONFIG_DIR to VITA3K_SAVES_DIR except "data", "lang", and "shaders-builtin"
                for item in listdir(VITA3K_CONFIG_DIR):
                    if item not in ['data', 'lang', 'shaders-builtin']:
                        item_path = path.join(VITA3K_CONFIG_DIR, item)
                        if path.isdir(item_path):
                            move(item_path, VITA3K_SAVES_DIR)

            # Create the config.yml file if it doesn't exist
            vita3kymlconfig = {}
            indent = 2
            block_seq_indent = 0
            if path.isfile(VITA3K_CONFIG_PATH):
                try:
                    from ruamel.yaml.util import load_yaml_guess_indent
                    with open(VITA3K_CONFIG_PATH, 'r') as stream:
                        vita3kymlconfig, indent, block_seq_indent = load_yaml_guess_indent(stream)
                except ImportError:
                    with open(VITA3K_CONFIG_PATH, 'r') as stream:
                        yaml = YAML()
                        vita3kymlconfig = yaml.load(stream)
                    indent = 2
                    block_seq_indent = 0

            if vita3kymlconfig is None:
                vita3kymlconfig = {}

            # ensure the correct path is set
            vita3kymlconfig["pref-path"] = VITA3K_SAVES_DIR

            # Set the renderer
            if system.isOptSet("vita3k_gfxbackend"):
                vita3kymlconfig["backend-renderer"] = system.config["vita3k_gfxbackend"]
            else:
                vita3kymlconfig["backend-renderer"] = "OpenGL"
            # Set the resolution multiplier
            if system.isOptSet("vita3k_resolution"):
                vita3kymlconfig["resolution-multiplier"] = int(system.config["vita3k_resolution"])
            else:
                vita3kymlconfig["resolution-multiplier"] = 1
            # Set FXAA
            if system.isOptSet("vita3k_fxaa") and system.getOptBoolean("vita3k_surface") == True:
                vita3kymlconfig["enable-fxaa"] = "true"
            else:
                vita3kymlconfig["enable-fxaa"] = "false"
            # Set VSync
            if system.isOptSet("vita3k_vsync") and system.getOptBoolean("vita3k_surface") == False:
                vita3kymlconfig["v-sync"] = "false"
            else:
                vita3kymlconfig["v-sync"] = "true"
            # Set the anisotropic filtering
            if system.isOptSet("vita3k_anisotropic"):
                vita3kymlconfig["anisotropic-filtering"] = int(system.config["vita3k_anisotropic"])
            else:
                vita3kymlconfig["anisotropic-filtering"] = 1
            # Set the linear filtering option
            if system.isOptSet("vita3k_linear") and system.getOptBoolean("vita3k_surface") == True:
                vita3kymlconfig["enable-linear-filter"] = "true"
            else:
                vita3kymlconfig["enable-linear-filter"] = "false"
            # Surface Sync
            if system.isOptSet("vita3k_surface") and system.getOptBoolean("vita3k_surface") == False:
                vita3kymlconfig["disable-surface-sync"] = "false"
            else:
                vita3kymlconfig["disable-surface-sync"] = "true"

            # Vita3k is fussy over its yml file
            # We try to match it as close as possible, but the 'vectors' cause yml formatting issues
            yaml = YAML()
            yaml.explicit_start = True
            yaml.explicit_end = True
            yaml.indent(mapping=indent, sequence=indent, offset=block_seq_indent)

            with open(VITA3K_CONFIG_PATH, 'w') as fp:
                yaml.dump(vita3kymlconfig, fp)

            # Simplify the rom name (strip the directory & extension)
            begin, end = rom.find('['), rom.rfind(']')
            smplromname = rom[begin+1: end]
            # because of the yml formatting, we don't allow Vita3k to modify it
            # using the -w & -f options prevents Vita3k from re-writing & prompting the user in GUI
            # we want to avoid that so roms load straight away
            if path.isdir(VITA3K_SAVES_DIR + '/ux0/app/' + smplromname):
                commandArray = [VITA3K_BIN_PATH, "-F", "-w", "-f", "-c", VITA3K_CONFIG_PATH, "-r", smplromname]
            else:
                # Game not installed yet, let's open the menu
                commandArray = [VITA3K_BIN_PATH, "-F", "-w", "-f", "-c", VITA3K_CONFIG_PATH, rom]

            return Command(
                        array=commandArray,
                        env={
                            'SDL_GAMECONTROLLERCONFIG': generate_sdl_controller_config(playersControllers)
                        })

    # Show mouse for touchscreen actions
    def getMouseMode(self, config, rom):
        if "vita3k_show_pointer" in config and config["vita3k_show_pointer"] == "0":
             return False
        else:
             return True

    def getInGameRatio(self, config, gameResolution, rom):
        return 16/9
