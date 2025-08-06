from generators.Generator import Generator
from Command import Command
from .devilutionxConfig import DEVILUTIONX_CONFIG_DIR, DEVILUTIONX_SAVES_DIR, DEVILUTIONX_ROMS_DIR, DEVILUTIONX_BIN_PATH
from controllers import generate_sdl_controller_config

class DevilutionXGenerator(Generator):

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        commandArray = [DEVILUTIONX_BIN_PATH, '--data-dir', DEVILUTIONX_ROMS_DIR,
                        '--config-dir', DEVILUTIONX_CONFIG_DIR, '--save-dir', DEVILUTIONX_SAVES_DIR]

        if rom.endswith('hellfire.mpq'):
            commandArray.append('--hellfire')
        elif rom.endswith('spawn.mpq'):
            commandArray.append('--spawn')
        else:
            commandArray.append('--diablo')

        if system.isOptSet('showFPS') and system.getOptBoolean('showFPS') == True:
            commandArray.append('-f')

        return Command(
                    array=commandArray,
                    env={
                        'SDL_GAMECONTROLLERCONFIG': generate_sdl_controller_config(playersControllers)
                    })
