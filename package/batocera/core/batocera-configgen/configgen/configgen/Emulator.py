import os
import batoceraFiles
from settings.unixSettings import UnixSettings
import xml.etree.ElementTree as ET
import yaml
import collections

from utils.logger import get_logger
eslog = get_logger(__name__)

class Emulator():
    def __init__(self, name, rom):
        self.name = name

        # read the configuration from the system name
        self.config = Emulator.get_system_config(self.name, "/usr/share/reglinux/configgen/configgen-defaults.yml", "/usr/share/reglinux/configgen/configgen-defaults-arch.yml")
        if "emulator" not in self.config or self.config["emulator"] == "":
            eslog.error("no emulator defined. exiting.")
            raise Exception("No emulator found")

        system_emulator = self.config["emulator"]
        system_core     = self.config["core"]

        gsname = self.game_settings_name(rom)

        # load configuration from system.conf
        recalSettings = UnixSettings(batoceraFiles.batoceraConf)
        globalSettings = recalSettings.loadAll('global')
        controllersSettings = recalSettings.loadAll('controllers', True)
        systemSettings = recalSettings.loadAll(self.name)
        folderSettings = recalSettings.loadAll(self.name + ".folder[\"" + os.path.dirname(rom) + "\"]")
        gameSettings = recalSettings.loadAll(self.name + "[\"" + gsname + "\"]")

        # add some other options
        displaySettings = recalSettings.loadAll('display')
        for opt in displaySettings:
            self.config["display." + opt] = displaySettings[opt]

        # update config
        Emulator.updateConfiguration(self.config, controllersSettings)
        Emulator.updateConfiguration(self.config, globalSettings)
        Emulator.updateConfiguration(self.config, systemSettings)
        Emulator.updateConfiguration(self.config, folderSettings)
        Emulator.updateConfiguration(self.config, gameSettings)
        self.updateFromESSettings()
        eslog.debug("uimode: {}".format(self.config['uimode']))

        # forced emulators ?
        self.config["emulator-forced"] = False
        self.config["core-forced"] = False
        if "emulator" in globalSettings or "emulator" in systemSettings or "emulator" in gameSettings:
            self.config["emulator-forced"] = True
        if "core" in globalSettings or "core" in systemSettings or "core" in gameSettings:
            self.config["core-forced"] = True

        # update renderconfig
        self.renderconfig = {}
        if "shaderset" in self.config:
            if self.config["shaderset"] != "none":
                if os.path.exists("/userdata/shaders/configs/" + self.config["shaderset"] + "/rendering-defaults.yml"):
                    self.renderconfig = Emulator.get_generic_config(self.name, "/userdata/shaders/configs/" + self.config["shaderset"] + "/rendering-defaults.yml", "/userdata/shaders/configs/" + self.config["shaderset"] + "/rendering-defaults-arch.yml")
                else:
                    self.renderconfig = Emulator.get_generic_config(self.name, "/usr/share/reglinux/shaders/configs/" + self.config["shaderset"] + "/rendering-defaults.yml", "/usr/share/reglinux/shaders/configs/" + self.config["shaderset"] + "/rendering-defaults-arch.yml")
            elif self.config["shaderset"] == "none":
                self.renderconfig = Emulator.get_generic_config(self.name, "/usr/share/reglinux/shaders/configs/rendering-defaults.yml", "/usr/share/reglinux/shaders/configs/rendering-defaults-arch.yml")

        # for compatibility with earlier Batocera versions, let's keep -renderer
        # but it should be reviewed when we refactor configgen (to Python3?)
        # so that we can fetch them from system.shader without -renderer
        systemSettings = recalSettings.loadAll(self.name + "-renderer")
        gameSettings = recalSettings.loadAll(self.name + "[\"" + gsname + "\"]" + "-renderer")

        # es only allow to update systemSettings and gameSettings in fact for the moment
        Emulator.updateConfiguration(self.renderconfig, systemSettings)
        Emulator.updateConfiguration(self.renderconfig, gameSettings)

    def game_settings_name(self,rom):

        rom = os.path.basename(rom)

        # sanitize rule by EmulationStation
        # see FileData::getConfigurationName() on reglinux-emulationstation
        rom = rom.replace('=','')
        rom = rom.replace('#','')
        eslog.info("game settings name: "+rom)
        return rom

    # to be updated for python3: https://gist.github.com/angstwad/bf22d1822c38a92ec0a9
    @staticmethod
    def dict_merge(dct, merge_dct):
        """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
        ``dct``.
        :param dct: dict onto which the merge is executed
        :param merge_dct: dct merged into dct
        :return: None
        """
        for k, v in merge_dct.items():
            if (k in dct and isinstance(dct[k], dict) and isinstance(merge_dct[k], collections.abc.Mapping)):
                Emulator.dict_merge(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]

    @staticmethod
    def get_generic_config(system, defaultyml, defaultarchyml):
        with open(defaultyml, 'r') as f:
            systems_default = yaml.load(f, Loader=yaml.CLoader)

        systems_default_arch = {}
        if os.path.exists(defaultarchyml):
            with open(defaultarchyml, 'r') as f:
                systems_default_arch = yaml.load(f, Loader=yaml.CLoader)
                if systems_default_arch is None:
                    systems_default_arch = {}
        dict_all = {}

        if "default" in systems_default:
            dict_all = systems_default["default"]

        if "default" in systems_default_arch:
            Emulator.dict_merge(dict_all, systems_default_arch["default"])

        if system in systems_default:
            Emulator.dict_merge(dict_all, systems_default[system])

        if system in systems_default_arch:
            Emulator.dict_merge(dict_all, systems_default_arch[system])

        return dict_all

    @staticmethod
    def get_system_config(system, defaultyml, defaultarchyml):
        dict_all = Emulator.get_generic_config(system, defaultyml, defaultarchyml)

        # options are in the yaml, not in the system structure
        # it is flat in the system.conf which is easier for the end user, but i prefer not flat in the yml files
        dict_result = {"emulator": dict_all["emulator"], "core": dict_all["core"]}
        if "options" in dict_all:
            Emulator.dict_merge(dict_result, dict_all["options"])
        return dict_result

    def isOptSet(self, key):
        if key in self.config:
            return True
        else:
            return False

    def getOptBoolean(self, key):
        true_values = {'1', 'true', 'on', 'enabled', True}
        value = self.config.get(key)

        if isinstance(value, str):
            value = value.lower()

        return value in true_values

    def getOptString(self, key):
        if key in self.config:
            if self.config[key]:
                return self.config[key]
        return ""

    @staticmethod
    def updateConfiguration(config, settings):
        # ignore all values "default", "auto", "" to take the system value instead
        # ideally, such value must not be in the configuration file
        # but historically some user have them
        toremove = [k for k in settings if settings[k] == "" or settings[k] == "default" or settings[k] == "auto"]
        for k in toremove: del settings[k]

        config.update(settings)

    # fps value is from es
    def updateFromESSettings(self):
        try:
            esConfig = ET.parse(batoceraFiles.esSettings)

            # showFPS
            try:
                drawframerate_value = esConfig.find("./bool[@name='DrawFramerate']").attrib["value"]
            except:
                drawframerate_value = 'false'
            if drawframerate_value not in ['false', 'true']:
                drawframerate_value = 'false'
            self.config['showFPS'] = drawframerate_value

            # uimode
            try:
                uimode_value = esConfig.find("./string[@name='UIMode']").attrib["value"]
            except:
                uimode_value = 'Full'
            if uimode_value not in ['Full', 'Kiosk', 'Kid']:
                uimode_value = 'Full'
            self.config['uimode'] = uimode_value

        except:
            self.config['showFPS'] = False
            self.config['uimode'] = "Full"

