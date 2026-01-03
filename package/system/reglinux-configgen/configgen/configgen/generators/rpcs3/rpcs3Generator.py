from configparser import ConfigParser
from os import makedirs, path
from re import match
from shutil import copy2, copytree

from configgen.Command import Command
from configgen.generators.Generator import Generator

try:
    from ruamel.yaml import YAML
except ImportError:
    print(
        "ruamel.yaml module not found. Please install it with: pip install ruamel.yaml",
    )
    raise
from subprocess import CalledProcessError, check_output
from typing import Any

from configgen.utils.logger import get_logger

from .rpcs3Config import (
    RPCS3_BIN_PATH,
    RPCS3_CONFIG_PATH,
    RPCS3_CURRENT_CONFIG_PATH,
    RPCS3_ICON_TARGET_DIR,
    RPCS3_PS3UPDAT_PATH,
)
from .rpcs3Controllers import generateControllerConfig

eslog = get_logger(__name__)


class Rpcs3Generator(Generator):
    # this emulator/core requires a X server to run
    def requiresX11(self):
        return True

    def generate(
        self,
        system: Any,
        rom: str,
        players_controllers: Any,
        metadata: Any,
        guns: Any,
        wheels: Any,
        game_resolution: dict[str, int],
    ) -> Command:
        generateControllerConfig(system, players_controllers, rom)

        # Taking care of the CurrentSettings.ini file
        if not path.exists(path.dirname(RPCS3_CURRENT_CONFIG_PATH)):
            makedirs(path.dirname(RPCS3_CURRENT_CONFIG_PATH))

        rpcsCurrentSettings = ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        rpcsCurrentSettings.optionxform = lambda optionstr: str(optionstr)
        if path.exists(RPCS3_CURRENT_CONFIG_PATH):
            rpcsCurrentSettings.read(RPCS3_CURRENT_CONFIG_PATH)

        # Sets Gui Settings to close completely and disables some popups
        if not rpcsCurrentSettings.has_section("main_window"):
            rpcsCurrentSettings.add_section("main_window")

        rpcsCurrentSettings.set("main_window", "confirmationBoxExitGame", "false")
        rpcsCurrentSettings.set("main_window", "infoBoxEnabledInstallPUP", "false")
        rpcsCurrentSettings.set("main_window", "infoBoxEnabledWelcome", "false")

        with open(RPCS3_CURRENT_CONFIG_PATH, "w") as configfile:
            rpcsCurrentSettings.write(configfile)

        if not path.exists(path.dirname(RPCS3_CONFIG_PATH)):
            makedirs(path.dirname(RPCS3_CONFIG_PATH))

        # Generate a default config if it doesn't exist otherwise just open the existing
        rpcs3ymlconfig = {}
        if path.isfile(RPCS3_CONFIG_PATH):
            with open(RPCS3_CONFIG_PATH) as stream:
                yaml = YAML(typ="unsafe", pure=True)
                rpcs3ymlconfig = yaml.load(stream)

        if rpcs3ymlconfig is None:  # in case the file is empty
            rpcs3ymlconfig = {}

        # Add Nodes if not in the file
        if "Core" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Core"] = {}
        if "VFS" not in rpcs3ymlconfig:
            rpcs3ymlconfig["VFS"] = {}
        if "Video" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Video"] = {}
        if "Audio" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Audio"] = {}
        if "Input/Output" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Input/Output"] = {}
        if "System" not in rpcs3ymlconfig:
            rpcs3ymlconfig["System"] = {}
        if "Net" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Net"] = {}
        if "Savestate" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Savestate"] = {}
        if "Miscellaneous" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Miscellaneous"] = {}
        if "Log" not in rpcs3ymlconfig:
            rpcs3ymlconfig["Log"] = {}

        # -= [Core] =-
        # Set the PPU Decoder based on config
        if system.isOptSet("rpcs3_ppudecoder"):
            rpcs3ymlconfig["Core"]["PPU Decoder"] = system.config["rpcs3_ppudecoder"]
        else:
            rpcs3ymlconfig["Core"]["PPU Decoder"] = "Recompiler (LLVM)"
        # Set the SPU Decoder based on config
        if system.isOptSet("rpcs3_spudecoder"):
            rpcs3ymlconfig["Core"]["SPU Decoder"] = system.config["rpcs3_spudecoder"]
        else:
            rpcs3ymlconfig["Core"]["SPU Decoder"] = "Recompiler (LLVM)"
        # Set the SPU XFloat Accuracy based on config
        rpcs3ymlconfig["Core"]["Accurate xfloat"] = False
        rpcs3ymlconfig["Core"]["Approximate xfloat"] = True
        # This is not an oversight. Relaxed xfloat is always set to "true" by the RPCS3 config menu.
        rpcs3ymlconfig["Core"]["Relaxed xfloat"] = True
        if system.isOptSet("rpcs3_spuxfloataccuracy"):
            if system.config["rpcs3_spuxfloataccuracy"] == "accurate":
                rpcs3ymlconfig["Core"]["Accurate xfloat"] = True
                rpcs3ymlconfig["Core"]["Approximate xfloat"] = False
            elif system.config["rpcs3_spuxfloataccuracy"] == "relaxed":
                rpcs3ymlconfig["Core"]["Accurate xfloat"] = False
                rpcs3ymlconfig["Core"]["Approximate xfloat"] = False
        # Set the Default Core Values we need
        # SPU Cache - disabled by default for better performance
        rpcs3ymlconfig["Core"]["SPU Cache"] = False
        # Preferred SPU Threads
        if system.isOptSet("rpcs3_sputhreads"):
            rpcs3ymlconfig["Core"]["Preferred SPU Threads"] = int(
                system.config["rpcs3_sputhreads"],
            )
        else:
            rpcs3ymlconfig["Core"]["Preferred SPU Threads"] = 0
        # SPU Loop Detection
        if system.isOptSet("rpcs3_spuloopdetection"):
            rpcs3ymlconfig["Core"]["SPU loop detection"] = system.getOptBoolean(
                "rpcs3_spuloopdetection",
            )
        else:
            rpcs3ymlconfig["Core"]["SPU loop detection"] = False
        # SPU Block Size
        if system.isOptSet("rpcs3_spublocksize"):
            rpcs3ymlconfig["Core"]["SPU Block Size"] = system.config[
                "rpcs3_spublocksize"
            ]
        else:
            rpcs3ymlconfig["Core"]["SPU Block Size"] = "Safe"
        # Max Power Saving CPU-Preemptions
        # values are maximum yields per frame threshold
        if system.isOptSet("rpcs3_maxcpu_preemptcount"):
            rpcs3ymlconfig["Core"]["Max CPU Preempt Count"] = int(
                system.config["rpcs3_maxcpu_preemptcount"],
            )
        else:
            rpcs3ymlconfig["Core"]["Max CPU Preempt Count"] = 0

        # -= [Video] =-
        # gfx backend - default to Vulkan
        # Check Vulkan first to be sure
        try:
            have_vulkan = check_output(
                ["/usr/bin/system-vulkan", "hasVulkan"], text=True,
            ).strip()
            if have_vulkan == "true":
                eslog.debug("Vulkan driver is available on the system.")
                if (
                    system.isOptSet("rpcs3_gfxbackend")
                    and system.config["rpcs3_gfxbackend"] == "OpenGL"
                ):
                    eslog.debug("User selected OpenGL")
                    rpcs3ymlconfig["Video"]["Renderer"] = "OpenGL"
                else:
                    rpcs3ymlconfig["Video"]["Renderer"] = "Vulkan"
                try:
                    have_discrete = check_output(
                        ["/usr/bin/system-vulkan", "hasDiscrete"], text=True,
                    ).strip()
                    if have_discrete == "true":
                        eslog.debug(
                            "A discrete GPU is available on the system. We will use that for performance",
                        )
                        try:
                            discrete_name = check_output(
                                ["/usr/bin/system-vulkan", "discreteName"], text=True,
                            ).strip()
                            if discrete_name != "":
                                eslog.debug(
                                    f"Using Discrete GPU Name: {discrete_name} for RPCS3",
                                )
                                if "Vulkan" not in rpcs3ymlconfig["Video"]:
                                    rpcs3ymlconfig["Video"]["Vulkan"] = {}
                                rpcs3ymlconfig["Video"]["Vulkan"]["Adapter"] = (
                                    discrete_name
                                )
                            else:
                                eslog.debug("Couldn't get discrete GPU Name")
                        except CalledProcessError:
                            eslog.debug("Error getting discrete GPU Name")
                    else:
                        eslog.debug(
                            "Discrete GPU is not available on the system. Trying integrated.",
                        )
                        have_integrated = check_output(
                            ["/usr/bin/system-vulkan", "hasIntegrated"], text=True,
                        ).strip()
                        if have_integrated == "true":
                            eslog.debug(
                                "Using integrated GPU to provide Vulkan. Beware of performance",
                            )
                            try:
                                integrated_name = check_output(
                                    ["/usr/bin/system-vulkan", "integratedName"],
                                    text=True,
                                ).strip()
                                if integrated_name != "":
                                    eslog.debug(
                                        f"Using Integrated GPU Name: {integrated_name} for RPCS3",
                                    )
                                    if "Vulkan" not in rpcs3ymlconfig["Video"]:
                                        rpcs3ymlconfig["Video"]["Vulkan"] = {}
                                    rpcs3ymlconfig["Video"]["Vulkan"]["Adapter"] = (
                                        integrated_name
                                    )
                                else:
                                    eslog.debug("Couldn't get integrated GPU name")
                            except CalledProcessError:
                                eslog.debug("Error getting integrated GPU index")
                        else:
                            eslog.debug(
                                "Integrated GPU is not available on the system. Cannot enable Vulkan.",
                            )
                except CalledProcessError:
                    eslog.debug("Error checking for discrete GPU.")
            else:
                eslog.debug(
                    "Vulkan driver is not available on the system. Falling back to OpenGL",
                )
                rpcs3ymlconfig["Video"]["Renderer"] = "OpenGL"
        except CalledProcessError:
            eslog.debug("Error checking for discrete GPU.")

        # System aspect ratio (the setting in the PS3 system itself, not the displayed ratio) a.k.a. TV mode.
        if system.isOptSet("rpcs3_ratio"):
            rpcs3ymlconfig["Video"]["Aspect ratio"] = system.config["rpcs3_ratio"]
        else:
            # If not set, see if the screen ratio is closer to 4:3 or 16:9 and pick that.
            rpcs3ymlconfig["Video"]["Aspect ratio"] = ":".join(
                map(str, getClosestRatio(game_resolution)),
            )
        # Shader compilation
        if system.isOptSet("rpcs3_shadermode"):
            rpcs3ymlconfig["Video"]["Shader Mode"] = system.config["rpcs3_shadermode"]
        else:
            rpcs3ymlconfig["Video"]["Shader Mode"] = "Async Shader Recompiler"
        # Vsync
        if system.isOptSet("rpcs3_vsync"):
            rpcs3ymlconfig["Video"]["VSync"] = system.getOptBoolean("rpcs3_vsync")
        else:
            rpcs3ymlconfig["Video"]["VSync"] = False
        # Stretch to display area
        if system.isOptSet("rpcs3_stretchdisplay"):
            rpcs3ymlconfig["Video"]["Stretch To Display Area"] = system.getOptBoolean(
                "rpcs3_stretchdisplay",
            )
        else:
            rpcs3ymlconfig["Video"]["Stretch To Display Area"] = False
        # Frame Limit
        # Frame limit checks for specific values("Auto", "Off", "30", "50", "59.94", "60")
        # Second Frame Limit can be any float/integer. 0 = disabled.
        if system.isOptSet("rpcs3_framelimit"):
            # Check for valid Frame Limit value, if it's not a Frame Limit value apply to Second Frame Limit
            if system.config["rpcs3_framelimit"] in ["Off", "30", "50", "59.94", "60"]:
                rpcs3ymlconfig["Video"]["Frame limit"] = system.config[
                    "rpcs3_framelimit"
                ]
                rpcs3ymlconfig["Video"]["Second Frame Limit"] = 0
            else:
                rpcs3ymlconfig["Video"]["Second Frame Limit"] = float(
                    system.config["rpcs3_framelimit"],
                )
                rpcs3ymlconfig["Video"]["Frame limit"] = "Off"
        else:
            rpcs3ymlconfig["Video"]["Frame limit"] = "Auto"
            rpcs3ymlconfig["Video"]["Second Frame Limit"] = 0
        # Write Color Buffers
        if system.isOptSet("rpcs3_colorbuffers"):
            rpcs3ymlconfig["Video"]["Write Color Buffers"] = system.getOptBoolean(
                "rpcs3_colorbuffers",
            )
        else:
            rpcs3ymlconfig["Video"]["Write Color Buffers"] = False
        # Disable Vertex Cache
        if system.isOptSet("rpcs3_vertexcache"):
            rpcs3ymlconfig["Video"]["Disable Vertex Cache"] = system.getOptBoolean(
                "rpcs3_vertexcache",
            )
        else:
            rpcs3ymlconfig["Video"]["Disable Vertex Cache"] = False
        # Anisotropic Filtering
        if system.isOptSet("rpcs3_anisotropic"):
            rpcs3ymlconfig["Video"]["Anisotropic Filter Override"] = int(
                system.config["rpcs3_anisotropic"],
            )
        else:
            rpcs3ymlconfig["Video"]["Anisotropic Filter Override"] = 0
        # MSAA
        if system.isOptSet("rpcs3_aa"):
            rpcs3ymlconfig["Video"]["MSAA"] = system.config["rpcs3_aa"]
        else:
            rpcs3ymlconfig["Video"]["MSAA"] = "Auto"
        # ZCULL
        if (
            system.isOptSet("rpcs3_zcull")
            and system.config["rpcs3_zcull"] == "Approximate"
        ):
            rpcs3ymlconfig["Video"]["Accurate ZCULL stats"] = False
            rpcs3ymlconfig["Video"]["Relaxed ZCULL Sync"] = False
        elif (
            system.isOptSet("rpcs3_zcull") and system.config["rpcs3_zcull"] == "Relaxed"
        ):
            rpcs3ymlconfig["Video"]["Accurate ZCULL stats"] = False
            rpcs3ymlconfig["Video"]["Relaxed ZCULL Sync"] = True
        else:
            rpcs3ymlconfig["Video"]["Accurate ZCULL stats"] = True
            rpcs3ymlconfig["Video"]["Relaxed ZCULL Sync"] = False
        # Shader Precision
        if system.isOptSet("rpcs3_shader"):
            rpcs3ymlconfig["Video"]["Shader Precision"] = system.config["rpcs3_shader"]
        else:
            rpcs3ymlconfig["Video"]["Shader Precision"] = "High"
            # Internal resolution (CHANGE AT YOUR OWN RISK)
            rpcs3ymlconfig["Video"]["Resolution"] = "1280x720"
        # Resolution scaling
        if system.isOptSet("rpcs3_resolution_scale"):
            rpcs3ymlconfig["Video"]["Resolution Scale"] = int(
                system.config["rpcs3_resolution_scale"],
            )
        else:
            rpcs3ymlconfig["Video"]["Resolution Scale"] = "100"
        # Output Scaling
        if system.isOptSet("rpcs3_scaling"):
            rpcs3ymlconfig["Video"]["Output Scaling Mode"] = system.config[
                "rpcs3_scaling"
            ]
        else:
            rpcs3ymlconfig["Video"]["Output Scaling Mode"] = "Bilinear"
        # Number of Shader Compilers
        if system.isOptSet("rpcs3_num_compilers"):
            rpcs3ymlconfig["Video"]["Shader Compiler Threads"] = int(
                system.config["rpcs3_num_compilers"],
            )
        else:
            rpcs3ymlconfig["Video"]["Shader Compiler Threads"] = 0
        # Multithreaded RSX
        if system.isOptSet("rpcs3_rsx"):
            rpcs3ymlconfig["Video"]["Multithreaded RSX"] = system.getOptBoolean(
                "rpcs3_rsx",
            )
        else:
            rpcs3ymlconfig["Video"]["Multithreaded RSX"] = False
        # Async Texture Streaming
        if system.isOptSet("rpcs3_async_texture"):
            rpcs3ymlconfig["Video"]["Asynchronous Texture Streaming 2"] = (
                system.getOptBoolean("rpcs3_async_texture")
            )
        else:
            rpcs3ymlconfig["Video"]["Asynchronous Texture Streaming 2"] = False

        # -= [Audio] =-
        # defaults
        rpcs3ymlconfig["Audio"]["Renderer"] = "Cubeb"
        rpcs3ymlconfig["Audio"]["Master Volume"] = 100
        # audio format
        if system.isOptSet("rpcs3_audio_format"):
            rpcs3ymlconfig["Audio"]["Audio Format"] = system.config[
                "rpcs3_audio_format"
            ]
        else:
            rpcs3ymlconfig["Audio"]["Audio Format"] = "Automatic"
        # convert to 16 bit
        if (
            system.isOptSet("rpcs3_audio_16bit")
            and system.config["rpcs3_audio_16bit"] == "True"
        ):
            rpcs3ymlconfig["Audio"]["Convert to 16 bit"] = True
        else:
            rpcs3ymlconfig["Audio"]["Convert to 16 bit"] = False
        # audio buffering
        if system.isOptSet("rpcs3_audiobuffer"):
            rpcs3ymlconfig["Audio"]["Enable Buffering"] = system.config[
                "rpcs3_audiobuffer"
            ]
        else:
            rpcs3ymlconfig["Audio"]["Enable Buffering"] = True
        # audio buffer duration
        if system.isOptSet("rpcs3_audiobuffer_duration"):
            rpcs3ymlconfig["Audio"]["Desired Audio Buffer Duration"] = int(
                system.config["rpcs3_audiobuffer_duration"],
            )
        else:
            rpcs3ymlconfig["Audio"]["Desired Audio Buffer Duration"] = 100
        # time stretching
        if (
            system.isOptSet("rpcs3_timestretch")
            and system.config["rpcs3_timestretch"] == "True"
        ):
            rpcs3ymlconfig["Audio"]["Enable Time Stretching"] = True
            rpcs3ymlconfig["Audio"]["Enable Buffering"] = True
        else:
            rpcs3ymlconfig["Audio"]["Enable Time Stretching"] = False
        # time stretching threshold
        if system.isOptSet("rpcs3_timestretch_threshold"):
            rpcs3ymlconfig["Audio"]["Time Stretching Threshold"] = int(
                system.config["rpcs3_timestretch_threshold"],
            )
        else:
            rpcs3ymlconfig["Audio"]["Time Stretching Threshold"] = 75

        # -= [Input/Output] =-
        # gun stuff
        if (
            system.isOptSet("use_guns")
            and system.getOptBoolean("use_guns")
            and len(guns) > 0
        ):
            rpcs3ymlconfig["Input/Output"]["Move"] = "Gun"
            rpcs3ymlconfig["Input/Output"]["Camera"] = "Fake"
            rpcs3ymlconfig["Input/Output"]["Camera type"] = "PS Eye"
        # Gun crosshairs
        if system.isOptSet("rpcs3_crosshairs"):
            rpcs3ymlconfig["Input/Output"]["Show move cursor"] = system.config[
                "rpcs3_crosshairs"
            ]
        else:
            rpcs3ymlconfig["Input/Output"]["Show move cursor"] = False

        # -= [Miscellaneous] =-
        rpcs3ymlconfig["Miscellaneous"]["Exit RPCS3 when process finishes"] = True
        rpcs3ymlconfig["Miscellaneous"]["Start games in fullscreen mode"] = True
        rpcs3ymlconfig["Miscellaneous"]["Show shader compilation hint"] = False
        rpcs3ymlconfig["Miscellaneous"]["Prevent display sleep while running games"] = (
            True
        )
        rpcs3ymlconfig["Miscellaneous"]["Show trophy popups"] = False

        with open(RPCS3_CONFIG_PATH, "w") as file:
            yaml = YAML(typ="unsafe", pure=True)
            yaml.default_flow_style = False
            yaml.dump(rpcs3ymlconfig, file)

        # copy icon files to config
        icon_source = "/usr/share/rpcs3/Icons/"
        icon_target = RPCS3_ICON_TARGET_DIR
        if not path.exists(icon_target):
            makedirs(icon_target)
        copytree(icon_source, icon_target, dirs_exist_ok=True, copy_function=copy2)

        # determine the rom name
        romName = None
        if rom.endswith(".psn"):
            with open(rom) as fp:
                for line in fp:
                    if len(line) >= 9:
                        romName = (
                            "/userdata/system/configs/rpcs3/dev_hdd0/game/"
                            + line.strip().upper()
                            + "/USRDIR/EBOOT.BIN"
                        )
        else:
            romName = rom + "/PS3_GAME/USRDIR/EBOOT.BIN"

        command_array = [str(RPCS3_BIN_PATH), romName]

        if not (system.isOptSet("rpcs3_gui") and system.getOptBoolean("rpcs3_gui")):
            command_array.append("--no-gui")

        # firmware not installed and available : instead of starting the game, install it
        if getFirmwareVersion() is None and path.exists(RPCS3_PS3UPDAT_PATH):
            command_array = [str(RPCS3_BIN_PATH), "--installfw", RPCS3_PS3UPDAT_PATH]

        return Command(array=command_array)


def getClosestRatio(game_resolution: dict[str, int]) -> tuple[int, int]:
    screenRatio = game_resolution["width"] / game_resolution["height"]
    if screenRatio < 1.6:
        return (4, 3)
    return (16, 9)


def get_in_game_ratio(config: Any, game_resolution: dict[str, int], rom: str) -> float:
    return 16 / 9


def getFirmwareVersion():
    try:
        with open(
            "/userdata/system/configs/rpcs3/dev_flash/vsh/etc/version.txt",
        ) as stream:
            lines = stream.readlines()
        for line in lines:
            matches = match("^release:(.*):", line)
            if matches:
                return matches[1]
    except Exception:
        return None
    return None
