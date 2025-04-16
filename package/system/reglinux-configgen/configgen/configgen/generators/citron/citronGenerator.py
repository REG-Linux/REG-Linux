#!/usr/bin/env python3

from generators.Generator import Generator
import Command
import os
import subprocess
import systemFiles
import configparser
from os import environ

from utils.logger import get_logger
eslog = get_logger(__name__)

class CitronGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        if not os.path.exists(systemFiles.CONF+"/citron"):
            os.makedirs(systemFiles.CONF+"/citron")

        CitronGenerator.writeCitronConfig(systemFiles.CONF + "/citron/qt-config.ini", system, playersControllers)

        commandArray = ["/usr/bin/citron-cmd", "-f", "-g", rom ]
        return Command.Command(array=commandArray, env={
            "XDG_DATA_HOME":systemFiles.SAVES + "/switch"})

    def writeCitronConfig(citronConfigFile, system, playersControllers):
        # pads
        citronButtonsMapping = {
            "button_a":      "a",
            "button_b":      "b",
            "button_x":      "x",
            "button_y":      "y",
            "button_dup":    "up",
            "button_ddown":  "down",
            "button_dleft":  "left",
            "button_dright": "right",
            "button_l":      "pageup",
            "button_r":      "pagedown",
            "button_plus":   "start",
            "button_minus":  "select",
            "button_sl":     "l",
            "button_sr":     "r",
            "button_zl":     "l2",
            "button_zr":     "r2",
            "button_lstick": "l3",
            "button_rstick": "r3",
            "button_home":   "hotkey"
        }

        citronAxisMapping = {
            "lstick":    "joystick1",
            "rstick":    "joystick2"
        }

        # ini file
        citronConfig = configparser.RawConfigParser()
        citronConfig.optionxform=str
        if os.path.exists(citronConfigFile):
            citronConfig.read(citronConfigFile)

        # UI section
        if not citronConfig.has_section("UI"):
            citronConfig.add_section("UI")
        citronConfig.set("UI", "fullscreen", "true")
        citronConfig.set("UI", "fullscreen\\default", "true")
        citronConfig.set("UI", "confirmClose", "false")
        citronConfig.set("UI", "confirmClose\\default", "false")
        citronConfig.set("UI", "firstStart", "false")
        citronConfig.set("UI", "firstStart\\default", "false")
        citronConfig.set("UI", "displayTitleBars", "false")
        citronConfig.set("UI", "displayTitleBars\\default", "false")
        citronConfig.set("UI", "enable_discord_presence", "false")
        citronConfig.set("UI", "enable_discord_presence\\default", "false")
        citronConfig.set("UI", "calloutFlags", "1")
        citronConfig.set("UI", "calloutFlags\\default", "false")
        citronConfig.set("UI", "confirmStop", "2")
        citronConfig.set("UI", "confirmStop\\default", "false")

        # Single Window Mode
        if system.isOptSet('citron_single_window'):
            citronConfig.set("UI", "singleWindowMode", system.config["citron_single_window"])
        else:
            citronConfig.set("UI", "singleWindowMode", "true")
        citronConfig.set("UI", "singleWindowMode\\default", "false")

        citronConfig.set("UI", "hideInactiveMouse", "true")
        citronConfig.set("UI", "hideInactiveMouse\\default", "false")

        # Roms path (need for load update/dlc)
        citronConfig.set("UI", "Paths\\gamedirs\\1\\deep_scan", "true")
        citronConfig.set("UI", "Paths\\gamedirs\\1\\deep_scan\\default", "false")
        citronConfig.set("UI", "Paths\\gamedirs\\1\\expanded", "true")
        citronConfig.set("UI", "Paths\\gamedirs\\1\\expanded\\default", "false")
        citronConfig.set("UI", "Paths\\gamedirs\\1\\path", "/userdata/roms/switch")
        citronConfig.set("UI", "Paths\\gamedirs\\size", "1")

        citronConfig.set("UI", "Screenshots\\enable_screenshot_save_as", "true")
        citronConfig.set("UI", "Screenshots\\enable_screenshot_save_as\\default", "false")
        citronConfig.set("UI", "Screenshots\\screenshot_path", "/userdata/screenshots")
        citronConfig.set("UI", "Screenshots\\screenshot_path\\default", "false")

        # Change controller exit
        citronConfig.set("UI", "Shortcuts\\Main%20Window\\Continue\\Pause%20Emulation\\Controller_KeySeq", "Home+Minus")
        citronConfig.set("UI", "Shortcuts\\Main%20Window\\Exit%20citron\\Controller_KeySeq", "Home+Plus")

        # Data Storage section
        if not citronConfig.has_section("Data%20Storage"):
            citronConfig.add_section("Data%20Storage")
        citronConfig.set("Data%20Storage", "dump_directory", "/userdata/system/configs/citron/dump")
        citronConfig.set("Data%20Storage", "dump_directory\\default", "false")

        citronConfig.set("Data%20Storage", "load_directory", "/userdata/system/configs/citron/load")
        citronConfig.set("Data%20Storage", "load_directory\\default", "false")

        citronConfig.set("Data%20Storage", "nand_directory", "/userdata/system/configs/citron/nand")
        citronConfig.set("Data%20Storage", "nand_directory\\default", "false")

        citronConfig.set("Data%20Storage", "sdmc_directory", "/userdata/system/configs/citron/sdmc")
        citronConfig.set("Data%20Storage", "sdmc_directory\\default", "false")

        citronConfig.set("Data%20Storage", "tas_directory", "/userdata/system/configs/citron/tas")
        citronConfig.set("Data%20Storage", "tas_directory\\default", "false")

        citronConfig.set("Data%20Storage", "use_virtual_sd", "true")
        citronConfig.set("Data%20Storage", "use_virtual_sd\\default", "false")

        # Core section
        if not citronConfig.has_section("Core"):
            citronConfig.add_section("Core")

        # Multicore
        citronConfig.set("Core", "use_multi_core", "true")
        citronConfig.set("Core", "use_multi_core\\default", "false")

        # Renderer section
        if not citronConfig.has_section("Renderer"):
            citronConfig.add_section("Renderer")

        # Aspect ratio
        if system.isOptSet('citron_ratio'):
            citronConfig.set("Renderer", "aspect_ratio", system.config["citron_ratio"])
        else:
            citronConfig.set("Renderer", "aspect_ratio", "0")
        citronConfig.set("Renderer", "aspect_ratio\\default", "false")

        # Graphical backend
        if system.isOptSet('citron_backend'):
            citronConfig.set("Renderer", "backend", system.config["citron_backend"])
            # Add vulkan logic
            if system.config["citron_backend"] == "1":
                try:
                    have_vulkan = subprocess.check_output(["/usr/bin/system-vulkan", "hasVulkan"], text=True).strip()
                    if have_vulkan == "true":
                        eslog.debug("Vulkan driver is available on the system.")
                        try:
                            have_discrete = subprocess.check_output(["/usr/bin/system-vulkan", "hasDiscrete"], text=True).strip()
                            if have_discrete == "true":
                                eslog.debug("A discrete GPU is available on the system. We will use that for performance")
                                try:
                                    discrete_index = subprocess.check_output(["/usr/bin/system-vulkan", "discreteIndex"], text=True).strip()
                                    if discrete_index != "":
                                        eslog.debug("Using Discrete GPU Index: {} for citron".format(discrete_index))
                                        citronConfig.set("Renderer", "vulkan_device", discrete_index)
                                        citronConfig.set("Renderer", "vulkan_device\\default", "true")
                                    else:
                                        eslog.debug("Couldn't get discrete GPU index, using default")
                                        citronConfig.set("Renderer", "vulkan_device", "0")
                                        citronConfig.set("Renderer", "vulkan_device\\default", "true")
                                except subprocess.CalledProcessError:
                                    eslog.debug("Error getting discrete GPU index")
                            else:
                                eslog.debug("Discrete GPU is not available on the system. Using default.")
                                citronConfig.set("Renderer", "vulkan_device", "0")
                                citronConfig.set("Renderer", "vulkan_device\\default", "true")
                        except subprocess.CalledProcessError:
                            eslog.debug("Error checking for discrete GPU.")
                except subprocess.CalledProcessError:
                    eslog.debug("Error executing system-vulkan script.")
        else:
            citronConfig.set("Renderer", "backend", "0")
        citronConfig.set("Renderer", "backend\\default", "false")

        # Async Shader compilation
        if system.isOptSet('citron_async_shaders'):
            citronConfig.set("Renderer", "use_asynchronous_shaders", system.config["citron_async_shaders"])
        else:
            citronConfig.set("Renderer", "use_asynchronous_shaders", "true")
        citronConfig.set("Renderer", "use_asynchronous_shaders\\default", "false")

        # Assembly shaders
        if system.isOptSet('citron_shaderbackend'):
            citronConfig.set("Renderer", "shader_backend", system.config["citron_shaderbackend"])
        else:
            citronConfig.set("Renderer", "shader_backend", "0")
        citronConfig.set("Renderer", "shader_backend\\default", "false")

        # Async Gpu Emulation
        if system.isOptSet('citron_async_gpu'):
            citronConfig.set("Renderer", "use_asynchronous_gpu_emulation", system.config["citron_async_gpu"])
        else:
            citronConfig.set("Renderer", "use_asynchronous_gpu_emulation", "true")
        citronConfig.set("Renderer", "use_asynchronous_gpu_emulation\\default", "false")

        # NVDEC Emulation
        if system.isOptSet('citron_nvdec_emu'):
            citronConfig.set("Renderer", "nvdec_emulation", system.config["citron_nvdec_emu"])
        else:
            citronConfig.set("Renderer", "nvdec_emulation", "2")
        citronConfig.set("Renderer", "nvdec_emulation\\default", "false")

        # GPU Accuracy
        if system.isOptSet('citron_accuracy'):
            citronConfig.set("Renderer", "gpu_accuracy", system.config["citron_accuracy"])
        else:
            citronConfig.set("Renderer", "gpu_accuracy", "0")
        citronConfig.set("Renderer", "gpu_accuracy\\default", "true")

        # Vsync
        if system.isOptSet('citron_vsync'):
            citronConfig.set("Renderer", "use_vsync", system.config["citron_vsync"])
        else:
            citronConfig.set("Renderer", "use_vsync", "1")
        citronConfig.set("Renderer", "use_vsync\\default", "false")

        # Max anisotropy
        if system.isOptSet('citron_anisotropy'):
            citronConfig.set("Renderer", "max_anisotropy", system.config["citron_anisotropy"])
        else:
            citronConfig.set("Renderer", "max_anisotropy", "0")
        citronConfig.set("Renderer", "max_anisotropy\\default", "false")

        # Resolution scaler
        if system.isOptSet('citron_scale'):
            citronConfig.set("Renderer", "resolution_setup", system.config["citron_scale"])
        else:
            citronConfig.set("Renderer", "resolution_setup", "2")
        citronConfig.set("Renderer", "resolution_setup\\default", "false")

        # Scaling filter
        if system.isOptSet('citron_scale_filter'):
            citronConfig.set("Renderer", "scaling_filter", system.config["citron_scale_filter"])
        else:
            citronConfig.set("Renderer", "scaling_filter", "1")
        citronConfig.set("Renderer", "scaling_filter\\default", "false")

        # Anti aliasing method
        if system.isOptSet('citron_aliasing_method'):
            citronConfig.set("Renderer", "anti_aliasing", system.config["citron_aliasing_method"])
        else:
            citronConfig.set("Renderer", "anti_aliasing", "0")
        citronConfig.set("Renderer", "anti_aliasing\\default", "false")

        # CPU Section
        if not citronConfig.has_section("Cpu"):
            citronConfig.add_section("Cpu")

        # CPU Accuracy
        if system.isOptSet('citron_cpuaccuracy'):
            citronConfig.set("Cpu", "cpu_accuracy", system.config["citron_cpuaccuracy"])
        else:
            citronConfig.set("Cpu", "cpu_accuracy", "0")
        citronConfig.set("Cpu", "cpu_accuracy\\default", "false")

        # System section
        if not citronConfig.has_section("System"):
            citronConfig.add_section("System")

        # Language
        if system.isOptSet('citron_language'):
            citronConfig.set("System", "language_index", system.config["citron_language"])
        else:
            citronConfig.set("System", "language_index", CitronGenerator.getCitronLangFromEnvironment())
        citronConfig.set("System", "language_index\\default", "false")

        # Region
        if system.isOptSet('citron_region'):
            citronConfig.set("System", "region_index", system.config["citron_region"])
        else:
            citronConfig.set("System", "region_index", CitronGenerator.getCitronRegionFromEnvironment())
        citronConfig.set("System", "region_index\\default", "false")

         # controls section
        if not citronConfig.has_section("Controls"):
            citronConfig.add_section("Controls")

        # Dock Mode
        if system.isOptSet('citron_dock_mode'):
            citronConfig.set("Controls", "use_docked_mode", system.config["citron_dock_mode"])
        else:
            citronConfig.set("Controls", "use_docked_mode", "true")
        citronConfig.set("Controls", "use_docked_mode\\default", "false")

        # Sound Mode
        if system.isOptSet('citron_sound_mode'):
            citronConfig.set("Controls", "sound_index", system.config["citron_sound_mode"])
        else:
            citronConfig.set("Controls", "sound_index", "1")
        citronConfig.set("Controls", "sound_index\\default", "false")

        # Timezone
        if system.isOptSet('citron_timezone'):
            citronConfig.set("Controls", "time_zone_index", system.config["citron_timezone"])
        else:
            citronConfig.set("Controls", "time_zone_index", "0")
        citronConfig.set("Controls", "time_zone_index\\default", "false")

        # controllers
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if system.isOptSet('p{}_pad'.format(nplayer-1)):
                citronConfig.set("Controls", "player_{}_type".format(nplayer-1), system.config["p{}_pad".format(nplayer)])
            else:
                citronConfig.set("Controls", "player_{}_type".format(nplayer-1), 0)
            citronConfig.set("Controls", "player_{}_type\\default".format(nplayer-1), "false")

            for x in citronButtonsMapping:
                citronConfig.set("Controls", "player_" + str(nplayer-1) + "_" + x, '"{}"'.format(CitronGenerator.setButton(citronButtonsMapping[x], pad.guid, pad.inputs, nplayer-1)))
            for x in citronAxisMapping:
                citronConfig.set("Controls", "player_" + str(nplayer-1) + "_" + x, '"{}"'.format(CitronGenerator.setAxis(citronAxisMapping[x], pad.guid, pad.inputs, nplayer-1)))
            citronConfig.set("Controls", "player_" + str(nplayer-1) + "_motionleft", '"[empty]"')
            citronConfig.set("Controls", "player_" + str(nplayer-1) + "_motionright", '"[empty]"')
            citronConfig.set("Controls", "player_" + str(nplayer-1) + "_connected", "true")
            citronConfig.set("Controls", "player_" + str(nplayer-1) + "_connected\\default", "false")
            citronConfig.set("Controls", "player_" + str(nplayer-1) + "_vibration_enabled", "true")
            citronConfig.set("Controls", "player_" + str(nplayer-1) + "_vibration_enabled\\default", "false")
            nplayer += 1

        citronConfig.set("Controls", "vibration_enabled", "true")
        citronConfig.set("Controls", "vibration_enabled\\default", "false")

        for y in range(nplayer, 9):
            citronConfig.set("Controls", "player_" + str(y-1) + "_connected", "false")
            citronConfig.set("Controls", "player_" + str(y-1) + "_connected\\default", "false")

        # telemetry section
        if not citronConfig.has_section("WebService"):
            citronConfig.add_section("WebService")
        citronConfig.set("WebService", "enable_telemetry", "false")
        citronConfig.set("WebService", "enable_telemetry\\default", "false")

        # Services section
        if not citronConfig.has_section("Services"):
            citronConfig.add_section("Services")
        citronConfig.set("Services", "bcat_backend", "none")
        citronConfig.set("Services", "bcat_backend\\default", "none")

        ### update the configuration file
        if not os.path.exists(os.path.dirname(citronConfigFile)):
            os.makedirs(os.path.dirname(citronConfigFile))
        with open(citronConfigFile, 'w') as configfile:
            citronConfig.write(configfile)

    @staticmethod
    def setButton(key, padGuid, padInputs, port):
        # it would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
        if key in padInputs:
            input = padInputs[key]

            if input.type == "button":
                return ("engine:sdl,button:{},guid:{},port:{}").format(input.id, padGuid, port)
            elif input.type == "hat":
                return ("engine:sdl,hat:{},direction:{},guid:{},port:{}").format(input.id, CitronGenerator.hatdirectionvalue(input.value), padGuid, port)
            elif input.type == "axis":
                return ("engine:sdl,threshold:{},axis:{},guid:{},port:{},invert:{}").format(0.5, input.id, padGuid, port, "+")
        return ""

    @staticmethod
    def setAxis(key, padGuid, padInputs, port):
        inputx = "0"
        inputy = "0"

        if key == "joystick1" and "joystick1left" in padInputs:
            inputx = padInputs["joystick1left"]
        elif key == "joystick2" and "joystick2left" in padInputs:
            inputx = padInputs["joystick2left"]

        if key == "joystick1" and "joystick1up" in padInputs:
                inputy = padInputs["joystick1up"]
        elif key == "joystick2" and "joystick2up" in padInputs:
            inputy = padInputs["joystick2up"]
        return ("engine:sdl,range:1.000000,deadzone:0.100000,invert_y:+,invert_x:+,offset_y:-0.000000,axis_y:{},offset_x:-0.000000,axis_x:{},guid:{},port:{}").format(inputy, inputx, padGuid, port)

    @staticmethod
    def hatdirectionvalue(value):
        if int(value) == 1:
            return "up"
        if int(value) == 4:
            return "down"
        if int(value) == 2:
            return "right"
        if int(value) == 8:
            return "left"
        else:
            return "unknown"

    @staticmethod
    def getCitronLangFromEnvironment():
        lang = environ['LANG'][:5]
        availableLanguages = { "en_US": 1, "fr_FR": 2, "de_DE": 3, "it_IT": 4, "es_ES": 5, "nl_NL": 8, "pt_PT": 9 }
        if lang in availableLanguages:
            return availableLanguages[lang]
        else:
            return availableLanguages["en_US"]

    @staticmethod
    def getCitronRegionFromEnvironment():
        lang = environ['LANG'][:5]
        availableRegions = { "en_US": 1, "ja_JP": 0 }
        if lang in availableRegions:
            return availableRegions[lang]
        else:
            return 2 # europe
