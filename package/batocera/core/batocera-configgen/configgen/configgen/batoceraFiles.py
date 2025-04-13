#!/usr/bin/env python

HOME_INIT = '/usr/share/reglinux/datainit/system/'
HOME = '/userdata/system'
CONF_INIT = HOME_INIT + '/configs'
CONF = HOME + '/configs'
EVMAPY = CONF + '/evmapy'
SAVES = '/userdata/saves'
SCREENSHOTS = '/userdata/screenshots'
RECORDINGS = '/userdata/recordings'
BIOS = '/userdata/bios'
OVERLAYS = '/userdata/overlays'
CACHE = '/userdata/system/cache'
ROMS = '/userdata/roms'

esInputs = CONF + '/emulationstation/gamecontrollerdb.txt'
esSettings = CONF + '/emulationstation/es_settings.cfg'
esGunsMetadata = "/usr/share/emulationstation/resources/gungames.xml"
esWheelsMetadata = "/usr/share/emulationstation/resources/wheelgames.xml"
esGamesMetadata = "/usr/share/emulationstation/resources/gamesdb.xml"
batoceraConf = HOME + '/system.conf'
logdir = HOME + '/logs/'

screenshotsDir = "/userdata/screenshots/"
savesDir = "/userdata/saves/"

overlaySystem = "/usr/share/reglinux/datainit/decorations"
overlayUser = "/userdata/decorations"
overlayConfigFile = "/userdata/system/configs/retroarch/overlay.cfg"

# This dict is indexed on the emulator name, not on the system
batoceraBins = {'dosbox_staging' : '/usr/bin/dosbox-staging'
              , 'dosboxx'        : '/usr/bin/dosbox-x'
              , 'libretro'       : '/usr/bin/retroarch'
              , 'moonlight'      : '/usr/bin/moonlight'
              , 'mupen64plus'    : '/usr/bin/mupen64plus'
              , 'flycast'        : '/usr/bin/flycast'
              , 'scummvm'        : '/usr/bin/scummvm'
              , 'vice'           : '/usr/bin/'
              , 'amiberry'       : '/usr/bin/amiberry'
              , 'hypseus-singe'  : '/usr/bin/hypseus'
              , 'melonds'        : '/usr/bin/melonDS'
              , 'rpcs3'          : '/usr/bin/rpcs3'
              , 'hatari'         : '/usr/bin/hatari'
              , 'supermodel'     : '/usr/bin/supermodel'
              , 'tsugaru'        : '/usr/bin/Tsugaru_CUI'
              , 'xemu'           : '/usr/bin/xemu'
              , 'gsplus'         : '/usr/bin/GSplus'
              , 'applewin'       : '/usr/bin/applewin'
              , 'fba2x'          : '/usr/bin/fba2x'
              , 'mednafen'       : '/usr/bin/mednafen'
}

daphneRomdir = ROMS + '/daphne'
singeRomdir = ROMS + '/singe'
hypseusDatadir = CONF + '/hypseus-singe'
hypseusConfig = hypseusDatadir+ '/hypinput.ini'
hypseusConfigfile = 'hypinput.ini'
hypseusSaves = SAVES + '/hypseus'

flycastCustom = CONF + '/flycast'
flycastMapping = flycastCustom + '/mappings'
flycastConfig = flycastCustom + '/emu.cfg'
flycastSaves = SAVES + '/dreamcast'
flycastBios = BIOS + '/dc'
flycastVMUBlank = '/usr/share/reglinux/configgen/data/dreamcast/vmu_save_blank.bin'
flycastVMUA1 = flycastSaves + '/flycast/vmu_save_A1.bin'
flycastVMUA2 = flycastSaves + '/flycast/vmu_save_A2.bin'

rpcs3Config = CONF
rpcs3Homedir = ROMS + '/ps3'
rpcs3Saves = SAVES
rpcs3CurrentConfig = CONF + '/rpcs3/GuiConfigs/CurrentSettings.ini'
rpcs3config = CONF + '/rpcs3/config.yml'
rpcs3configInput = CONF + '/rpcs3/config_input.yml'
rpcs3configevdev = CONF + '/rpcs3/InputConfigs/Evdev/Default Profile.yml'

supermodelCustom = CONF + '/supermodel'
supermodelIni = supermodelCustom + '/Supermodel.ini'

sdlpopConfigDir = CONF + '/sdlpop'
sdlpopSrcCfg = sdlpopConfigDir + '/SDLPoP.cfg'
sdlpopSrcIni = sdlpopConfigDir + '/SDLPoP.ini'
sdlpopDestCfg = '/usr/share/sdlpop/SDLPoP.cfg'
sdlpopDestIni = '/usr/share/sdlpop/SDLPoP.ini'
