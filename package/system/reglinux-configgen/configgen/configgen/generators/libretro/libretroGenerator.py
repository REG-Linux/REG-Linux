from os import chdir
from pathlib import Path
from shutil import copyfile
from typing import Any

from configgen.Command import Command
from configgen.generators.Generator import Generator
from configgen.settings import UnixSettings
from configgen.systemFiles import OVERLAYS
from configgen.utils.logger import get_logger
from configgen.utils.videoMode import getAltDecoration, getGLVendor, getGLVersion

from .libretroConfig import (
    coreForceSlangShaders,
    retroarchBin,
    retroarchCores,
    retroarchCustom,
    retroarchRoot,
    writeLibretroConfig,
)
from .libretroRetroarchCustom import (
    generateRetroarchCustom,
    generateRetroarchCustomPathes,
)

eslog = get_logger(__name__)


class LibretroGenerator(Generator):
    def supportsInternalBezels(self):
        return True

    # Main entry of the module
    # Configure retroarch and return a command
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
        # Get the graphics backend first
        gfxBackend = getGFXBackend(system)

        # Get the shader before writing the config, we may need to disable bezels based on the shader.
        renderConfig = system.renderconfig
        altDecoration = getAltDecoration(system.name, rom, "retroarch")
        gameShader = None
        shaderBezel = False
        video_shader = None

        if altDecoration == "0":
            if "shader" in renderConfig:
                gameShader = renderConfig["shader"]
        else:
            if ("shader-" + str(altDecoration)) in renderConfig:
                gameShader = renderConfig["shader-" + str(altDecoration)]
            else:
                gameShader = renderConfig["shader"]
        if "shader" in renderConfig and gameShader is not None:
            if (gfxBackend == "glcore" or gfxBackend == "vulkan") or (
                system.config["core"] in coreForceSlangShaders
            ):
                shaderFilename = gameShader + ".slangp"
            else:
                shaderFilename = gameShader + ".glslp"
            eslog.debug(f"searching shader {shaderFilename}")
            shader_path = Path("/userdata/shaders") / shaderFilename
            if shader_path.exists():
                video_shader_dir = "/userdata/shaders"
                eslog.debug(f"shader {shaderFilename} found in /userdata/shaders")
            else:
                video_shader_dir = "/usr/share/reglinux/shaders"
            video_shader = str(Path(video_shader_dir) / shaderFilename)
            # If the shader filename contains noBezel, activate Shader Bezel mode.
            if "noBezel" in video_shader:
                shaderBezel = True

        # Settings system default config file if no user defined one
        if "configfile" not in system.config:
            # Using system config file
            system.config["configfile"] = retroarchCustom
            # Create retroarchcustom.cfg if does not exists
            if not Path(retroarchCustom).is_file():
                generateRetroarchCustom()
            #  Write controllers configuration files
            retroconfig = UnixSettings(retroarchCustom, separator=" ")

            # force pathes
            generateRetroarchCustomPathes(retroconfig)
            # Write configuration to retroarchcustom.cfg
            if "bezel" not in system.config or system.config["bezel"] == "":
                bezel = None
            else:
                bezel = system.config["bezel"]
            # some systems (ie gw) won't bezels
            if system.isOptSet("forceNoBezel") and system.getOptBoolean("forceNoBezel"):
                bezel = None

            writeLibretroConfig(
                self,
                retroconfig,
                system,
                players_controllers,
                metadata,
                guns,
                wheels,
                rom,
                bezel,
                shaderBezel,
                game_resolution,
                gfxBackend,
            )
            retroconfig.write()

            # duplicate config to mapping files while ra now split in 2 parts
            remapconfigDir = Path(retroarchRoot) / "config" / "remaps" / "common"
            if not remapconfigDir.exists():
                remapconfigDir.mkdir(parents=True, exist_ok=True)
            copyfile(retroarchCustom, str(remapconfigDir / "common.rmp"))

        # Retroarch core on the filesystem
        retroarchCore = retroarchCores + system.config["core"] + "_libretro.so"

        # for each core, a file /usr/lib/<core>.info must exit, otherwise, info such as rewinding/netplay will not work
        # to do a global check : cd /usr/lib/libretro && for i in *.so; do INF=$(echo $i | sed -e s+/usr/lib/libretro+/usr/share/libretro/info+ -e s+\.so+.info+); test -e "$INF" || echo $i; done
        infoFile = (
            "/usr/share/libretro/info/" + system.config["core"] + "_libretro.info"
        )
        if not Path(infoFile).exists():
            raise Exception("missing file " + infoFile)

        romName = Path(rom).name

        # The command to run
        dontAppendROM = False
        # For the NeoGeo CD (lr-fbneo) it is necessary to add the parameter: --subsystem neocd
        if system.name == "neogeocd" and system.config["core"] == "fbneo":
            command_array = [
                retroarchBin,
                "-L",
                retroarchCore,
                "--subsystem",
                "neocd",
                "--config",
                system.config["configfile"],
            ]
        # PURE zip games uses the same commandarray of all cores. .pc and .rom  uses owns
        elif system.name == "dos":
            romDOSName, romExtension = Path(romName).stem, Path(romName).suffix
            if romExtension == ".dos" or romExtension == ".pc":
                rom_path = Path(rom)
                rom_bat_path = rom_path / (romDOSName + ".bat")
                dosbox_bat_path = rom_path / "dosbox.bat"

                if rom_bat_path.exists() and " " not in romDOSName:
                    exe = str(rom_bat_path)
                elif dosbox_bat_path.exists() and not rom_bat_path.exists():
                    exe = str(dosbox_bat_path)
                else:
                    exe = rom
                command_array = [
                    retroarchBin,
                    "-L",
                    retroarchCore,
                    "--config",
                    system.config["configfile"],
                    exe,
                ]
                dontAppendROM = True
            else:
                command_array = [
                    retroarchBin,
                    "-L",
                    retroarchCore,
                    "--config",
                    system.config["configfile"],
                ]
        # Pico-8 multi-carts (might work only with official Lexaloffe engine right now)
        elif system.name == "pico8":
            romext = Path(romName).suffix
            if romext.lower() == ".m3u":
                with open(rom) as fpin:
                    lines = fpin.readlines()
                rom = str(Path(rom).parent / lines[0].strip())
            command_array = [
                retroarchBin,
                "-L",
                retroarchCore,
                "--config",
                system.config["configfile"],
            ]
        # vitaquake2 - choose core based on directory
        elif system.name == "vitaquake2":
            directory_path = str(Path(rom).parent)
            if "xatrix" in directory_path:
                system.config["core"] = "vitaquake2-xatrix"
            elif "rogue" in directory_path:
                system.config["core"] = "vitaquake2-rogue"
            elif "zaero" in directory_path:
                system.config["core"] = "vitaquake2-zaero"
            # set the updated core name
            retroarchCore = retroarchCores + system.config["core"] + "_libretro.so"
            command_array = [
                retroarchBin,
                "-L",
                retroarchCore,
                "--config",
                system.config["configfile"],
            ]
        # super mario wars - verify assets from Content Downloader
        elif system.name == "superbroswar":
            romdir = str(Path(rom).parent)
            assetdirs = [
                "music/world/Standard",
                "music/game/Standard/Special",
                "music/game/Standard/Menu",
                "filters",
                "worlds/KingdomHigh",
                "worlds/MrIsland",
                "worlds/Sky World",
                "worlds/Smb3",
                "worlds/Simple",
                "worlds/screenshots",
                "worlds/Flurry World",
                "worlds/MixedRiver",
                "worlds/Contest",
                "gfx/skins",
                "gfx/packs/Retro/fonts",
                "gfx/packs/Retro/modeobjects",
                "gfx/packs/Retro/eyecandy",
                "gfx/packs/Retro/awards",
                "gfx/packs/Retro/powerups",
                "gfx/packs/Retro/menu",
                "gfx/packs/Classic/projectiles",
                "gfx/packs/Classic/fonts",
                "gfx/packs/Classic/modeobjects",
                "gfx/packs/Classic/world",
                "gfx/packs/Classic/world/thumbnail",
                "gfx/packs/Classic/world/preview",
                "gfx/packs/Classic/modeskins",
                "gfx/packs/Classic/hazards",
                "gfx/packs/Classic/blocks",
                "gfx/packs/Classic/backgrounds",
                "gfx/packs/Classic/tilesets/SMB2",
                "gfx/packs/Classic/tilesets/Expanded",
                "gfx/packs/Classic/tilesets/SMB1",
                "gfx/packs/Classic/tilesets/Classic",
                "gfx/packs/Classic/tilesets/SMB3",
                "gfx/packs/Classic/tilesets/SuperMarioWorld",
                "gfx/packs/Classic/tilesets/YoshisIsland",
                "gfx/packs/Classic/eyecandy",
                "gfx/packs/Classic/awards",
                "gfx/packs/Classic/powerups",
                "gfx/packs/Classic/menu",
                "gfx/leveleditor",
                "gfx/docs",
                "sfx/packs/Classic",
                "sfx/announcer/Mario",
                "maps/tour",
                "maps/cache",
                "maps/screenshots",
                "maps/special",
                "tours",
            ]
            try:
                for assetdir in assetdirs:
                    chdir(f"{romdir}/{assetdir}")
                chdir(romdir)
            except FileNotFoundError:
                eslog.error(
                    "ERROR: Game assets not installed. You can get them from the Batocera Content Downloader."
                )
                raise

            command_array = [
                retroarchBin,
                "-L",
                retroarchCore,
                "--config",
                system.config["configfile"],
            ]
        else:
            command_array = [
                retroarchBin,
                "-L",
                retroarchCore,
                "--config",
                system.config["configfile"],
            ]

        configToAppend = []

        # Custom configs - per core
        customCfg = f"{retroarchRoot}/{system.name}.cfg"
        if Path(customCfg).is_file():
            configToAppend.append(customCfg)

        # Custom configs - per game
        customGameCfg = f"{retroarchRoot}/{system.name}/{romName}.cfg"
        if Path(customGameCfg).is_file():
            configToAppend.append(customGameCfg)

        # Overlay management
        overlayFile = f"{OVERLAYS}/{system.name}/{romName}.cfg"
        if Path(overlayFile).is_file():
            configToAppend.append(overlayFile)

        if "shader" in renderConfig and gameShader is not None:
            command_array.extend(["--set-shader", video_shader])

        # Generate the append
        if configToAppend:
            command_array.extend(["--appendconfig", "|".join(configToAppend)])

        # Netplay mode
        if "netplay.mode" in system.config:
            if system.config["netplay.mode"] == "host":
                command_array.append("--host")
            elif (
                system.config["netplay.mode"] == "client"
                or system.config["netplay.mode"] == "spectator"
            ):
                command_array.extend(["--connect", system.config["netplay.server.ip"]])
            if "netplay.server.port" in system.config:
                command_array.extend(["--port", system.config["netplay.server.port"]])
            if "netplay.server.session" in system.config:
                command_array.extend(
                    ["--mitm-session", system.config["netplay.server.session"]]
                )
            if "netplay.nickname" in system.config:
                command_array.extend(["--nick", system.config["netplay.nickname"]])

        # Verbose logs
        command_array.extend(["--verbose"])

        if system.name == "scummvm":
            rom = str(Path(rom).parent / romName[0:-8])

        if system.name == "reminiscence":
            with open(rom) as file:
                first_line = file.readline().strip()
            directory_path = "/".join(rom.split("/")[:-1])
            rom = f"{directory_path}/{first_line}"

        # Use command line instead of ROM file for MAME variants
        if system.config["core"] in ["mame", "same_cdi"]:
            dontAppendROM = True
            command_array.append(f"/var/run/cmdfiles/{Path(rom).stem}.cmd")

        if not dontAppendROM:
            command_array.append(rom)

        return Command(array=command_array)


def getGFXBackend(system: Any) -> str | Any:
    # Start with the selected option
    # Pick glcore or gl based on drivers if not selected
    VALID_BACKENDS = {
        "gl",
        "glcore",
        "vulkan",
        "opengl",
    }  # opengl is legacy alias for gl

    if system.isOptSet("gfxbackend"):
        backend = system.config["gfxbackend"]
        # Validate backend value
        if backend not in VALID_BACKENDS:
            eslog.warning(f"Invalid gfxbackend '{backend}', falling back to 'gl'")
            backend = "gl"
        setManually = True
    else:
        setManually = False
        # glvendor check first, to avoid a 2nd testing on intel boards
        if getGLVendor() in ["nvidia", "amd"] and getGLVersion() >= 3.1:
            backend = "glcore"
        else:
            backend = "gl"

    # Retroarch has flipped between using opengl or gl, correct the setting here if needed.
    if backend == "opengl":
        backend = "gl"

    # Don't change based on core if manually selected.
    if not setManually:
        # If set to glcore or gl, override setting for certain cores that require one or the other
        core = system.config["core"]
        if backend == "gl" and core in ["kronos", "melonds", "beetle-psx-hw"]:
            backend = "glcore"
        if backend == "glcore" and core in ["parallel_n64", "yabasanshiro"]:
            backend = "gl"

    return backend
