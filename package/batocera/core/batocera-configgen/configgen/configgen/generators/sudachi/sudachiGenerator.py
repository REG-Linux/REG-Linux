#!/usr/bin/env python

from generators.Generator import Generator
import Command
import os
import batoceraFiles
import configparser
from os import environ
import subprocess

from utils.logger import get_logger
eslog = get_logger(__name__)

class SudachiGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        if not os.path.exists(batoceraFiles.CONF+"/sudachi"):
            os.makedirs(batoceraFiles.CONF+"/sudachi")

        SudachiGenerator.writeSudachiConfig(batoceraFiles.CONF + "/sudachi/qt-config.ini", system, playersControllers)

        commandArray = ["/usr/bin/sudachi", "-f", "-g", rom ]
        return Command.Command(array=commandArray, env={
            "XDG_CONFIG_HOME":batoceraFiles.CONF, \
            "XDG_DATA_HOME":batoceraFiles.SAVES + "/switch", \
            "XDG_CACHE_HOME":batoceraFiles.CACHE, \
            "QT_QPA_PLATFORM":"xcb"})

    def writeSudachiConfig(sudachiConfigFile, system, playersControllers):
        # pads
        sudachiButtonsMapping = {
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

        sudachiAxisMapping = {
            "lstick":    "joystick1",
            "rstick":    "joystick2"
        }

        # ini file
        sudachiConfig = configparser.RawConfigParser()
        sudachiConfig.optionxform=str
        if os.path.exists(sudachiConfigFile):
            sudachiConfig.read(sudachiConfigFile)

        # UI section
        if not sudachiConfig.has_section("UI"):
            sudachiConfig.add_section("UI")
        sudachiConfig.set("UI", "fullscreen", "true")
        sudachiConfig.set("UI", "fullscreen\\default", "true")
        sudachiConfig.set("UI", "confirmClose", "false")
        sudachiConfig.set("UI", "confirmClose\\default", "false")
        sudachiConfig.set("UI", "firstStart", "false")
        sudachiConfig.set("UI", "firstStart\\default", "false")
        sudachiConfig.set("UI", "displayTitleBars", "false")
        sudachiConfig.set("UI", "displayTitleBars\\default", "false")
        sudachiConfig.set("UI", "enable_discord_presence", "false")
        sudachiConfig.set("UI", "enable_discord_presence\\default", "false")
        sudachiConfig.set("UI", "calloutFlags", "1")
        sudachiConfig.set("UI", "calloutFlags\\default", "false")
        sudachiConfig.set("UI", "confirmStop", "2")
        sudachiConfig.set("UI", "confirmStop\\default", "false")

        # Single Window Mode
        if system.isOptSet('sudachi_single_window'):
            sudachiConfig.set("UI", "singleWindowMode", system.config["sudachi_single_window"])
        else:
            sudachiConfig.set("UI", "singleWindowMode", "true")
        sudachiConfig.set("UI", "singleWindowMode\\default", "false")

        sudachiConfig.set("UI", "hideInactiveMouse", "true")
        sudachiConfig.set("UI", "hideInactiveMouse\\default", "false")

        # Roms path (need for load update/dlc)
        sudachiConfig.set("UI", "Paths\\gamedirs\\1\\deep_scan", "true")
        sudachiConfig.set("UI", "Paths\\gamedirs\\1\\deep_scan\\default", "false")
        sudachiConfig.set("UI", "Paths\\gamedirs\\1\\expanded", "true")
        sudachiConfig.set("UI", "Paths\\gamedirs\\1\\expanded\\default", "false")
        sudachiConfig.set("UI", "Paths\\gamedirs\\1\\path", "/userdata/roms/switch")
        sudachiConfig.set("UI", "Paths\\gamedirs\\size", "1")

        sudachiConfig.set("UI", "Screenshots\\enable_screenshot_save_as", "true")
        sudachiConfig.set("UI", "Screenshots\\enable_screenshot_save_as\\default", "false")
        sudachiConfig.set("UI", "Screenshots\\screenshot_path", "/userdata/screenshots")
        sudachiConfig.set("UI", "Screenshots\\screenshot_path\\default", "false")

        # Change controller exit
        sudachiConfig.set("UI", "Shortcuts\\Main%20Window\\Continue\\Pause%20Emulation\\Controller_KeySeq", "Home+Minus")
        sudachiConfig.set("UI", "Shortcuts\\Main%20Window\\Exit%20sudachi\\Controller_KeySeq", "Home+Plus")

        # Data Storage section
        if not sudachiConfig.has_section("Data%20Storage"):
            sudachiConfig.add_section("Data%20Storage")
        sudachiConfig.set("Data%20Storage", "dump_directory", "/userdata/system/configs/sudachi/dump")
        sudachiConfig.set("Data%20Storage", "dump_directory\\default", "false")

        sudachiConfig.set("Data%20Storage", "load_directory", "/userdata/system/configs/sudachi/load")
        sudachiConfig.set("Data%20Storage", "load_directory\\default", "false")

        sudachiConfig.set("Data%20Storage", "nand_directory", "/userdata/system/configs/sudachi/nand")
        sudachiConfig.set("Data%20Storage", "nand_directory\\default", "false")

        sudachiConfig.set("Data%20Storage", "sdmc_directory", "/userdata/system/configs/sudachi/sdmc")
        sudachiConfig.set("Data%20Storage", "sdmc_directory\\default", "false")

        sudachiConfig.set("Data%20Storage", "tas_directory", "/userdata/system/configs/sudachi/tas")
        sudachiConfig.set("Data%20Storage", "tas_directory\\default", "false")

        sudachiConfig.set("Data%20Storage", "use_virtual_sd", "true")
        sudachiConfig.set("Data%20Storage", "use_virtual_sd\\default", "false")

        # Core section
        if not sudachiConfig.has_section("Core"):
            sudachiConfig.add_section("Core")

        # Multicore
        sudachiConfig.set("Core", "use_multi_core", "true")
        sudachiConfig.set("Core", "use_multi_core\\default", "false")

        # Renderer section
        if not sudachiConfig.has_section("Renderer"):
            sudachiConfig.add_section("Renderer")

        # Aspect ratio
        if system.isOptSet('sudachi_ratio'):
            sudachiConfig.set("Renderer", "aspect_ratio", system.config["sudachi_ratio"])
        else:
            sudachiConfig.set("Renderer", "aspect_ratio", "0")
        sudachiConfig.set("Renderer", "aspect_ratio\\default", "false")

        # Graphical backend
        if system.isOptSet('sudachi_backend'):
            sudachiConfig.set("Renderer", "backend", system.config["sudachi_backend"])
            # Add vulkan logic
            if system.config["sudachi_backend"] == "1":
                try:
                    have_vulkan = subprocess.check_output(["/usr/bin/batocera-vulkan", "hasVulkan"], text=True).strip()
                    if have_vulkan == "true":
                        eslog.debug("Vulkan driver is available on the system.")
                        try:
                            have_discrete = subprocess.check_output(["/usr/bin/batocera-vulkan", "hasDiscrete"], text=True).strip()
                            if have_discrete == "true":
                                eslog.debug("A discrete GPU is available on the system. We will use that for performance")
                                try:
                                    discrete_index = subprocess.check_output(["/usr/bin/batocera-vulkan", "discreteIndex"], text=True).strip()
                                    if discrete_index != "":
                                        eslog.debug("Using Discrete GPU Index: {} for Sudachi".format(discrete_index))
                                        sudachiConfig.set("Renderer", "vulkan_device", discrete_index)
                                        sudachiConfig.set("Renderer", "vulkan_device\\default", "true")
                                    else:
                                        eslog.debug("Couldn't get discrete GPU index, using default")
                                        sudachiConfig.set("Renderer", "vulkan_device", "0")
                                        sudachiConfig.set("Renderer", "vulkan_device\\default", "true")
                                except subprocess.CalledProcessError:
                                    eslog.debug("Error getting discrete GPU index")
                            else:
                                eslog.debug("Discrete GPU is not available on the system. Using default.")
                                sudachiConfig.set("Renderer", "vulkan_device", "0")
                                sudachiConfig.set("Renderer", "vulkan_device\\default", "true")
                        except subprocess.CalledProcessError:
                            eslog.debug("Error checking for discrete GPU.")
                except subprocess.CalledProcessError:
                    eslog.debug("Error executing batocera-vulkan script.")
        else:
            sudachiConfig.set("Renderer", "backend", "0")
        sudachiConfig.set("Renderer", "backend\\default", "false")

        # Async Shader compilation
        if system.isOptSet('sudachi_async_shaders'):
            sudachiConfig.set("Renderer", "use_asynchronous_shaders", system.config["sudachi_async_shaders"])
        else:
            sudachiConfig.set("Renderer", "use_asynchronous_shaders", "true")
        sudachiConfig.set("Renderer", "use_asynchronous_shaders\\default", "false")

        # Assembly shaders
        if system.isOptSet('sudachi_shaderbackend'):
            sudachiConfig.set("Renderer", "shader_backend", system.config["sudachi_shaderbackend"])
        else:
            sudachiConfig.set("Renderer", "shader_backend", "0")
        sudachiConfig.set("Renderer", "shader_backend\\default", "false")

        # Async Gpu Emulation
        if system.isOptSet('sudachi_async_gpu'):
            sudachiConfig.set("Renderer", "use_asynchronous_gpu_emulation", system.config["sudachi_async_gpu"])
        else:
            sudachiConfig.set("Renderer", "use_asynchronous_gpu_emulation", "true")
        sudachiConfig.set("Renderer", "use_asynchronous_gpu_emulation\\default", "false")

        # NVDEC Emulation
        if system.isOptSet('sudachi_nvdec_emu'):
            sudachiConfig.set("Renderer", "nvdec_emulation", system.config["sudachi_nvdec_emu"])
        else:
            sudachiConfig.set("Renderer", "nvdec_emulation", "2")
        sudachiConfig.set("Renderer", "nvdec_emulation\\default", "false")

        # GPU Accuracy
        if system.isOptSet('sudachi_accuracy'):
            sudachiConfig.set("Renderer", "gpu_accuracy", system.config["sudachi_accuracy"])
        else:
            sudachiConfig.set("Renderer", "gpu_accuracy", "0")
        sudachiConfig.set("Renderer", "gpu_accuracy\\default", "true")

        # Vsync
        if system.isOptSet('sudachi_vsync'):
            sudachiConfig.set("Renderer", "use_vsync", system.config["sudachi_vsync"])
        else:
            sudachiConfig.set("Renderer", "use_vsync", "1")
        sudachiConfig.set("Renderer", "use_vsync\\default", "false")

        # Max anisotropy
        if system.isOptSet('sudachi_anisotropy'):
            sudachiConfig.set("Renderer", "max_anisotropy", system.config["sudachi_anisotropy"])
        else:
            sudachiConfig.set("Renderer", "max_anisotropy", "0")
        sudachiConfig.set("Renderer", "max_anisotropy\\default", "false")

        # Resolution scaler
        if system.isOptSet('sudachi_scale'):
            sudachiConfig.set("Renderer", "resolution_setup", system.config["sudachi_scale"])
        else:
            sudachiConfig.set("Renderer", "resolution_setup", "2")
        sudachiConfig.set("Renderer", "resolution_setup\\default", "false")

        # Scaling filter
        if system.isOptSet('sudachi_scale_filter'):
            sudachiConfig.set("Renderer", "scaling_filter", system.config["sudachi_scale_filter"])
        else:
            sudachiConfig.set("Renderer", "scaling_filter", "1")
        sudachiConfig.set("Renderer", "scaling_filter\\default", "false")

        # Anti aliasing method
        if system.isOptSet('sudachi_aliasing_method'):
            sudachiConfig.set("Renderer", "anti_aliasing", system.config["sudachi_aliasing_method"])
        else:
            sudachiConfig.set("Renderer", "anti_aliasing", "0")
        sudachiConfig.set("Renderer", "anti_aliasing\\default", "false")

        # CPU Section
        if not sudachiConfig.has_section("Cpu"):
            sudachiConfig.add_section("Cpu")

        # CPU Accuracy
        if system.isOptSet('sudachi_cpuaccuracy'):
            sudachiConfig.set("Cpu", "cpu_accuracy", system.config["sudachi_cpuaccuracy"])
        else:
            sudachiConfig.set("Cpu", "cpu_accuracy", "0")
        sudachiConfig.set("Cpu", "cpu_accuracy\\default", "false")

        # System section
        if not sudachiConfig.has_section("System"):
            sudachiConfig.add_section("System")

        # Language
        if system.isOptSet('sudachi_language'):
            sudachiConfig.set("System", "language_index", system.config["sudachi_language"])
        else:
            sudachiConfig.set("System", "language_index", SudachiGenerator.getSudachiLangFromEnvironment())
        sudachiConfig.set("System", "language_index\\default", "false")

        # Region
        if system.isOptSet('sudachi_region'):
            sudachiConfig.set("System", "region_index", system.config["sudachi_region"])
        else:
            sudachiConfig.set("System", "region_index", SudachiGenerator.getSudachiRegionFromEnvironment())
        sudachiConfig.set("System", "region_index\\default", "false")

         # controls section
        if not sudachiConfig.has_section("Controls"):
            sudachiConfig.add_section("Controls")

        # Dock Mode
        if system.isOptSet('sudachi_dock_mode'):
            sudachiConfig.set("Controls", "use_docked_mode", system.config["sudachi_dock_mode"])
        else:
            sudachiConfig.set("Controls", "use_docked_mode", "true")
        sudachiConfig.set("Controls", "use_docked_mode\\default", "false")

        # Sound Mode
        if system.isOptSet('sudachi_sound_mode'):
            sudachiConfig.set("Controls", "sound_index", system.config["sudachi_sound_mode"])
        else:
            sudachiConfig.set("Controls", "sound_index", "1")
        sudachiConfig.set("Controls", "sound_index\\default", "false")

        # Timezone
        if system.isOptSet('sudachi_timezone'):
            sudachiConfig.set("Controls", "time_zone_index", system.config["sudachi_timezone"])
        else:
            sudachiConfig.set("Controls", "time_zone_index", "0")
        sudachiConfig.set("Controls", "time_zone_index\\default", "false")

        # controllers
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if system.isOptSet('p{}_pad'.format(nplayer-1)):
                sudachiConfig.set("Controls", "player_{}_type".format(nplayer-1), system.config["p{}_pad".format(nplayer)])
            else:
                sudachiConfig.set("Controls", "player_{}_type".format(nplayer-1), 0)
            sudachiConfig.set("Controls", "player_{}_type\default".format(nplayer-1), "false")

            for x in sudachiButtonsMapping:
                sudachiConfig.set("Controls", "player_" + str(nplayer-1) + "_" + x, '"{}"'.format(SudachiGenerator.setButton(sudachiButtonsMapping[x], pad.guid, pad.inputs, nplayer-1)))
            for x in sudachiAxisMapping:
                sudachiConfig.set("Controls", "player_" + str(nplayer-1) + "_" + x, '"{}"'.format(SudachiGenerator.setAxis(sudachiAxisMapping[x], pad.guid, pad.inputs, nplayer-1)))
            sudachiConfig.set("Controls", "player_" + str(nplayer-1) + "_motionleft", '"[empty]"')
            sudachiConfig.set("Controls", "player_" + str(nplayer-1) + "_motionright", '"[empty]"')
            sudachiConfig.set("Controls", "player_" + str(nplayer-1) + "_connected", "true")
            sudachiConfig.set("Controls", "player_" + str(nplayer-1) + "_connected\default", "false")
            sudachiConfig.set("Controls", "player_" + str(nplayer-1) + "_vibration_enabled", "true")
            sudachiConfig.set("Controls", "player_" + str(nplayer-1) + "_vibration_enabled\\default", "false")
            nplayer += 1

        sudachiConfig.set("Controls", "vibration_enabled", "true")
        sudachiConfig.set("Controls", "vibration_enabled\\default", "false")

        for y in range(nplayer, 9):
            sudachiConfig.set("Controls", "player_" + str(y-1) + "_connected", "false")
            sudachiConfig.set("Controls", "player_" + str(y-1) + "_connected\default", "false")

        # telemetry section
        if not sudachiConfig.has_section("WebService"):
            sudachiConfig.add_section("WebService")
        sudachiConfig.set("WebService", "enable_telemetry", "false")
        sudachiConfig.set("WebService", "enable_telemetry\\default", "false")

        # Services section
        if not sudachiConfig.has_section("Services"):
            sudachiConfig.add_section("Services")
        sudachiConfig.set("Services", "bcat_backend", "none")
        sudachiConfig.set("Services", "bcat_backend\\default", "none")

        ### update the configuration file
        if not os.path.exists(os.path.dirname(sudachiConfigFile)):
            os.makedirs(os.path.dirname(sudachiConfigFile))
        with open(sudachiConfigFile, 'w') as configfile:
            sudachiConfig.write(configfile)

    @staticmethod
    def setButton(key, padGuid, padInputs, port):
        # it would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
        if key in padInputs:
            input = padInputs[key]

            if input.type == "button":
                return ("engine:sdl,button:{},guid:{},port:{}").format(input.id, padGuid, port)
            elif input.type == "hat":
                return ("engine:sdl,hat:{},direction:{},guid:{},port:{}").format(input.id, SudachiGenerator.hatdirectionvalue(input.value), padGuid, port)
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
    def getSudachiLangFromEnvironment():
        lang = environ['LANG'][:5]
        availableLanguages = { "en_US": 1, "fr_FR": 2, "de_DE": 3, "it_IT": 4, "es_ES": 5, "nl_NL": 8, "pt_PT": 9 }
        if lang in availableLanguages:
            return availableLanguages[lang]
        else:
            return availableLanguages["en_US"]

    @staticmethod
    def getSudachiRegionFromEnvironment():
        lang = environ['LANG'][:5]
        availableRegions = { "en_US": 1, "ja_JP": 0 }
        if lang in availableRegions:
            return availableRegions[lang]
        else:
            return 2 # europe
