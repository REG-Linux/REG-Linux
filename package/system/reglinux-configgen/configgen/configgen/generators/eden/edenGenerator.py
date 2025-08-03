from generators.Generator import Generator
from Command import Command
import os
import subprocess
import configparser
from os import environ
from systemFiles import CONF

from utils.logger import get_logger
eslog = get_logger(__name__)

class EdenGenerator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(self, system, rom, playersControllers, metadata, guns, wheels, gameResolution):

        if not os.path.exists(CONF+"/eden"):
            os.makedirs(CONF+"/eden")

        EdenGenerator.writeEdenConfig(CONF + "/eden/qt-config.ini", system, playersControllers)

        commandArray = ["/usr/bin/eden-cli", "-f", "-g", rom ]
        return Command(array=commandArray)

    def writeEdenConfig(configFile, system, playersControllers):
        # pads
        edenButtonsMapping = {
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

        edenAxisMapping = {
            "lstick":    "joystick1",
            "rstick":    "joystick2"
        }

        # ini file
        edenConfig = configparser.RawConfigParser()
        edenConfig.optionxform=lambda optionstr: str(optionstr)
        if os.path.exists(configFile):
            edenConfig.read(configFile)

        # UI section
        if not edenConfig.has_section("UI"):
            edenConfig.add_section("UI")
        edenConfig.set("UI", "fullscreen", "true")
        edenConfig.set("UI", "fullscreen\\default", "true")
        edenConfig.set("UI", "confirmClose", "false")
        edenConfig.set("UI", "confirmClose\\default", "false")
        edenConfig.set("UI", "firstStart", "false")
        edenConfig.set("UI", "firstStart\\default", "false")
        edenConfig.set("UI", "displayTitleBars", "false")
        edenConfig.set("UI", "displayTitleBars\\default", "false")
        edenConfig.set("UI", "enable_discord_presence", "false")
        edenConfig.set("UI", "enable_discord_presence\\default", "false")
        edenConfig.set("UI", "calloutFlags", "1")
        edenConfig.set("UI", "calloutFlags\\default", "false")
        edenConfig.set("UI", "confirmStop", "2")
        edenConfig.set("UI", "confirmStop\\default", "false")

        # Single Window Mode
        if system.isOptSet('eden_single_window'):
            edenConfig.set("UI", "singleWindowMode", system.config["eden_single_window"])
        else:
            edenConfig.set("UI", "singleWindowMode", "true")
        edenConfig.set("UI", "singleWindowMode\\default", "false")

        edenConfig.set("UI", "hideInactiveMouse", "true")
        edenConfig.set("UI", "hideInactiveMouse\\default", "false")

        # Roms path (need for load update/dlc)
        edenConfig.set("UI", "Paths\\gamedirs\\1\\deep_scan", "true")
        edenConfig.set("UI", "Paths\\gamedirs\\1\\deep_scan\\default", "false")
        edenConfig.set("UI", "Paths\\gamedirs\\1\\expanded", "true")
        edenConfig.set("UI", "Paths\\gamedirs\\1\\expanded\\default", "false")
        edenConfig.set("UI", "Paths\\gamedirs\\1\\path", "/userdata/roms/switch")
        edenConfig.set("UI", "Paths\\gamedirs\\size", "1")

        edenConfig.set("UI", "Screenshots\\enable_screenshot_save_as", "true")
        edenConfig.set("UI", "Screenshots\\enable_screenshot_save_as\\default", "false")
        edenConfig.set("UI", "Screenshots\\screenshot_path", "/userdata/screenshots")
        edenConfig.set("UI", "Screenshots\\screenshot_path\\default", "false")

        # Change controller exit
        edenConfig.set("UI", "Shortcuts\\Main%20Window\\Continue\\Pause%20Emulation\\Controller_KeySeq", "Home+Minus")
        edenConfig.set("UI", "Shortcuts\\Main%20Window\\Exit%20eden\\Controller_KeySeq", "Home+Plus")

        # Data Storage section
        if not edenConfig.has_section("Data%20Storage"):
            edenConfig.add_section("Data%20Storage")
        edenConfig.set("Data%20Storage", "dump_directory", "/userdata/system/configs/eden/dump")
        edenConfig.set("Data%20Storage", "dump_directory\\default", "false")

        edenConfig.set("Data%20Storage", "load_directory", "/userdata/system/configs/eden/load")
        edenConfig.set("Data%20Storage", "load_directory\\default", "false")

        edenConfig.set("Data%20Storage", "nand_directory", "/userdata/system/configs/eden/nand")
        edenConfig.set("Data%20Storage", "nand_directory\\default", "false")

        edenConfig.set("Data%20Storage", "sdmc_directory", "/userdata/system/configs/eden/sdmc")
        edenConfig.set("Data%20Storage", "sdmc_directory\\default", "false")

        edenConfig.set("Data%20Storage", "tas_directory", "/userdata/system/configs/eden/tas")
        edenConfig.set("Data%20Storage", "tas_directory\\default", "false")

        edenConfig.set("Data%20Storage", "use_virtual_sd", "true")
        edenConfig.set("Data%20Storage", "use_virtual_sd\\default", "false")

        # Core section
        if not edenConfig.has_section("Core"):
            edenConfig.add_section("Core")

        # Multicore
        edenConfig.set("Core", "use_multi_core", "true")
        edenConfig.set("Core", "use_multi_core\\default", "false")

        # Renderer section
        if not edenConfig.has_section("Renderer"):
            edenConfig.add_section("Renderer")

        # Aspect ratio
        if system.isOptSet('eden_ratio'):
            edenConfig.set("Renderer", "aspect_ratio", system.config["eden_ratio"])
        else:
            edenConfig.set("Renderer", "aspect_ratio", "0")
        edenConfig.set("Renderer", "aspect_ratio\\default", "false")

        # Graphical backend
        if system.isOptSet('eden_backend'):
            edenConfig.set("Renderer", "backend", system.config["eden_backend"])
            # Add vulkan logic
            if system.config["eden_backend"] == "1":
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
                                        eslog.debug("Using Discrete GPU Index: {} for eden".format(discrete_index))
                                        edenConfig.set("Renderer", "vulkan_device", discrete_index)
                                        edenConfig.set("Renderer", "vulkan_device\\default", "true")
                                    else:
                                        eslog.debug("Couldn't get discrete GPU index, using default")
                                        edenConfig.set("Renderer", "vulkan_device", "0")
                                        edenConfig.set("Renderer", "vulkan_device\\default", "true")
                                except subprocess.CalledProcessError:
                                    eslog.debug("Error getting discrete GPU index")
                            else:
                                eslog.debug("Discrete GPU is not available on the system. Using default.")
                                edenConfig.set("Renderer", "vulkan_device", "0")
                                edenConfig.set("Renderer", "vulkan_device\\default", "true")
                        except subprocess.CalledProcessError:
                            eslog.debug("Error checking for discrete GPU.")
                except subprocess.CalledProcessError:
                    eslog.debug("Error executing system-vulkan script.")
        else:
            edenConfig.set("Renderer", "backend", "0")
        edenConfig.set("Renderer", "backend\\default", "false")

        # Async Shader compilation
        if system.isOptSet('eden_async_shaders'):
            edenConfig.set("Renderer", "use_asynchronous_shaders", system.config["eden_async_shaders"])
        else:
            edenConfig.set("Renderer", "use_asynchronous_shaders", "true")
        edenConfig.set("Renderer", "use_asynchronous_shaders\\default", "false")

        # Assembly shaders
        if system.isOptSet('eden_shaderbackend'):
            edenConfig.set("Renderer", "shader_backend", system.config["eden_shaderbackend"])
        else:
            edenConfig.set("Renderer", "shader_backend", "0")
        edenConfig.set("Renderer", "shader_backend\\default", "false")

        # Async Gpu Emulation
        if system.isOptSet('eden_async_gpu'):
            edenConfig.set("Renderer", "use_asynchronous_gpu_emulation", system.config["eden_async_gpu"])
        else:
            edenConfig.set("Renderer", "use_asynchronous_gpu_emulation", "true")
        edenConfig.set("Renderer", "use_asynchronous_gpu_emulation\\default", "false")

        # NVDEC Emulation
        if system.isOptSet('eden_nvdec_emu'):
            edenConfig.set("Renderer", "nvdec_emulation", system.config["eden_nvdec_emu"])
        else:
            edenConfig.set("Renderer", "nvdec_emulation", "2")
        edenConfig.set("Renderer", "nvdec_emulation\\default", "false")

        # GPU Accuracy
        if system.isOptSet('eden_accuracy'):
            edenConfig.set("Renderer", "gpu_accuracy", system.config["eden_accuracy"])
        else:
            edenConfig.set("Renderer", "gpu_accuracy", "0")
        edenConfig.set("Renderer", "gpu_accuracy\\default", "true")

        # Vsync
        if system.isOptSet('eden_vsync'):
            edenConfig.set("Renderer", "use_vsync", system.config["eden_vsync"])
        else:
            edenConfig.set("Renderer", "use_vsync", "1")
        edenConfig.set("Renderer", "use_vsync\\default", "false")

        # Max anisotropy
        if system.isOptSet('eden_anisotropy'):
            edenConfig.set("Renderer", "max_anisotropy", system.config["eden_anisotropy"])
        else:
            edenConfig.set("Renderer", "max_anisotropy", "0")
        edenConfig.set("Renderer", "max_anisotropy\\default", "false")

        # Resolution scaler
        if system.isOptSet('eden_scale'):
            edenConfig.set("Renderer", "resolution_setup", system.config["eden_scale"])
        else:
            edenConfig.set("Renderer", "resolution_setup", "2")
        edenConfig.set("Renderer", "resolution_setup\\default", "false")

        # Scaling filter
        if system.isOptSet('eden_scale_filter'):
            edenConfig.set("Renderer", "scaling_filter", system.config["eden_scale_filter"])
        else:
            edenConfig.set("Renderer", "scaling_filter", "1")
        edenConfig.set("Renderer", "scaling_filter\\default", "false")

        # Anti aliasing method
        if system.isOptSet('eden_aliasing_method'):
            edenConfig.set("Renderer", "anti_aliasing", system.config["eden_aliasing_method"])
        else:
            edenConfig.set("Renderer", "anti_aliasing", "0")
        edenConfig.set("Renderer", "anti_aliasing\\default", "false")

        # CPU Section
        if not edenConfig.has_section("Cpu"):
            edenConfig.add_section("Cpu")

        # CPU Accuracy
        if system.isOptSet('eden_cpuaccuracy'):
            edenConfig.set("Cpu", "cpu_accuracy", system.config["eden_cpuaccuracy"])
        else:
            edenConfig.set("Cpu", "cpu_accuracy", "0")
        edenConfig.set("Cpu", "cpu_accuracy\\default", "false")

        # System section
        if not edenConfig.has_section("System"):
            edenConfig.add_section("System")

        # Language
        if system.isOptSet('eden_language'):
            edenConfig.set("System", "language_index", system.config["eden_language"])
        else:
            edenConfig.set("System", "language_index", EdenGenerator.getLangFromEnvironment())
        edenConfig.set("System", "language_index\\default", "false")

        # Region
        if system.isOptSet('eden_region'):
            edenConfig.set("System", "region_index", system.config["eden_region"])
        else:
            edenConfig.set("System", "region_index", EdenGenerator.getRegionFromEnvironment())
        edenConfig.set("System", "region_index\\default", "false")

         # controls section
        if not edenConfig.has_section("Controls"):
            edenConfig.add_section("Controls")

        # Dock Mode
        if system.isOptSet('eden_dock_mode'):
            edenConfig.set("Controls", "use_docked_mode", system.config["eden_dock_mode"])
        else:
            edenConfig.set("Controls", "use_docked_mode", "true")
        edenConfig.set("Controls", "use_docked_mode\\default", "false")

        # Sound Mode
        if system.isOptSet('eden_sound_mode'):
            edenConfig.set("Controls", "sound_index", system.config["eden_sound_mode"])
        else:
            edenConfig.set("Controls", "sound_index", "1")
        edenConfig.set("Controls", "sound_index\\default", "false")

        # Timezone
        if system.isOptSet('eden_timezone'):
            edenConfig.set("Controls", "time_zone_index", system.config["eden_timezone"])
        else:
            edenConfig.set("Controls", "time_zone_index", "0")
        edenConfig.set("Controls", "time_zone_index\\default", "false")

        # controllers
        nplayer = 1
        for playercontroller, pad in sorted(playersControllers.items()):
            if system.isOptSet('p{}_pad'.format(nplayer-1)):
                edenConfig.set("Controls", "player_{}_type".format(nplayer-1), system.config["p{}_pad".format(nplayer)])
            else:
                edenConfig.set("Controls", "player_{}_type".format(nplayer-1), 0)
            edenConfig.set("Controls", "player_{}_type\\default".format(nplayer-1), "false")

            for x in edenButtonsMapping:
                edenConfig.set("Controls", "player_" + str(nplayer-1) + "_" + x, '"{}"'.format(EdenGenerator.setButton(edenButtonsMapping[x], pad.guid, pad.inputs, nplayer-1)))
            for x in edenAxisMapping:
                edenConfig.set("Controls", "player_" + str(nplayer-1) + "_" + x, '"{}"'.format(EdenGenerator.setAxis(edenAxisMapping[x], pad.guid, pad.inputs, nplayer-1)))
            edenConfig.set("Controls", "player_" + str(nplayer-1) + "_motionleft", '"[empty]"')
            edenConfig.set("Controls", "player_" + str(nplayer-1) + "_motionright", '"[empty]"')
            edenConfig.set("Controls", "player_" + str(nplayer-1) + "_connected", "true")
            edenConfig.set("Controls", "player_" + str(nplayer-1) + "_connected\\default", "false")
            edenConfig.set("Controls", "player_" + str(nplayer-1) + "_vibration_enabled", "true")
            edenConfig.set("Controls", "player_" + str(nplayer-1) + "_vibration_enabled\\default", "false")
            nplayer += 1

        edenConfig.set("Controls", "vibration_enabled", "true")
        edenConfig.set("Controls", "vibration_enabled\\default", "false")

        for y in range(nplayer, 9):
            edenConfig.set("Controls", "player_" + str(y-1) + "_connected", "false")
            edenConfig.set("Controls", "player_" + str(y-1) + "_connected\\default", "false")

        # telemetry section
        if not edenConfig.has_section("WebService"):
            edenConfig.add_section("WebService")
        edenConfig.set("WebService", "enable_telemetry", "false")
        edenConfig.set("WebService", "enable_telemetry\\default", "false")

        # Services section
        if not edenConfig.has_section("Services"):
            edenConfig.add_section("Services")
        edenConfig.set("Services", "bcat_backend", "none")
        edenConfig.set("Services", "bcat_backend\\default", "none")

        ### update the configuration file
        if not os.path.exists(os.path.dirname(configFile)):
            os.makedirs(os.path.dirname(configFile))
        with open(configFile, 'w') as file:
            edenConfig.write(file)

    @staticmethod
    def setButton(key, padGuid, padInputs, port):
        # it would be better to pass the joystick num instead of the guid because 2 joysticks may have the same guid
        if key in padInputs:
            input = padInputs[key]

            if input.type == "button":
                return ("engine:sdl,button:{},guid:{},port:{}").format(input.id, padGuid, port)
            elif input.type == "hat":
                return ("engine:sdl,hat:{},direction:{},guid:{},port:{}").format(input.id, EdenGenerator.hatdirectionvalue(input.value), padGuid, port)
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
    def getLangFromEnvironment():
        lang = environ['LANG'][:5]
        availableLanguages = { "en_US": 1, "fr_FR": 2, "de_DE": 3, "it_IT": 4, "es_ES": 5, "nl_NL": 8, "pt_PT": 9 }
        if lang in availableLanguages:
            return availableLanguages[lang]
        else:
            return availableLanguages["en_US"]

    @staticmethod
    def getRegionFromEnvironment():
        lang = environ['LANG'][:5]
        availableRegions = { "en_US": 1, "ja_JP": 0 }
        if lang in availableRegions:
            return availableRegions[lang]
        else:
            return 2 # europe
