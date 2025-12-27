import configparser
from os import environ
from pathlib import Path
from typing import Any

from configgen.Command import Command
from configgen.generators.Generator import Generator

from . import dolphinTriforceConfig, dolphinTriforceControllers


class DolphinTriforceGenerator(Generator):
    # this emulator/core requires X server to run
    def requiresX11(self) -> bool:
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
        ini_path = Path(dolphinTriforceConfig.dolphinTriforceIni)
        if not ini_path.parent.exists():
            ini_path.parent.mkdir(parents=True, exist_ok=True)

        # Dir required for saves
        saves_path = Path(dolphinTriforceConfig.dolphinTriforceData) / "StateSaves"
        if not saves_path.exists():
            saves_path.mkdir(parents=True, exist_ok=True)

        dolphinTriforceControllers.generateControllerConfig(
            system, players_controllers, rom
        )

        ## dolphin.ini ##

        dolphinTriforceSettings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        dolphinTriforceSettings.optionxform = lambda optionstr: str(optionstr)
        if Path(dolphinTriforceConfig.dolphinTriforceIni).exists():
            dolphinTriforceSettings.read(dolphinTriforceConfig.dolphinTriforceIni)

        # Sections
        if not dolphinTriforceSettings.has_section("General"):
            dolphinTriforceSettings.add_section("General")
        if not dolphinTriforceSettings.has_section("Core"):
            dolphinTriforceSettings.add_section("Core")
        if not dolphinTriforceSettings.has_section("Interface"):
            dolphinTriforceSettings.add_section("Interface")
        if not dolphinTriforceSettings.has_section("Analytics"):
            dolphinTriforceSettings.add_section("Analytics")
        if not dolphinTriforceSettings.has_section("Display"):
            dolphinTriforceSettings.add_section("Display")

        # Define default games path
        if "ISOPaths" not in dolphinTriforceSettings["General"]:
            dolphinTriforceSettings.set(
                "General", "ISOPath0", str(Path("/userdata/roms/triforce"))
            )
            dolphinTriforceSettings.set("General", "ISOPaths", "1")
        if "GCMPathes" not in dolphinTriforceSettings["General"]:
            dolphinTriforceSettings.set(
                "General", "GCMPath0", str(Path("/userdata/roms/triforce"))
            )
            dolphinTriforceSettings.set("General", "GCMPathes", "1")

        # Save file location
        if "MemcardAPath" not in dolphinTriforceSettings["Core"]:
            dolphinTriforceSettings.set(
                "Core",
                "MemcardAPath",
                str(Path("/userdata/saves/dolphin-triforce/GC/MemoryCardA.USA.raw")),
            )
            dolphinTriforceSettings.set(
                "Core",
                "MemcardBPath",
                str(Path("/userdata/saves/dolphin-triforce/GC/MemoryCardB.USA.raw")),
            )

        # Draw or not FPS
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            dolphinTriforceSettings.set("General", "ShowLag", "True")
            dolphinTriforceSettings.set("General", "ShowFrameCount", "True")
        else:
            dolphinTriforceSettings.set("General", "ShowLag", "False")
            dolphinTriforceSettings.set("General", "ShowFrameCount", "False")

        # Don't ask about statistics
        dolphinTriforceSettings.set("Analytics", "PermissionAsked", "True")

        # PanicHandlers displaymessages
        dolphinTriforceSettings.set("Interface", "UsePanicHandlers", "False")

        # Disable OSD Messages
        if system.isOptSet("disable_osd_messages") and system.getOptBoolean(
            "disable_osd_messages"
        ):
            dolphinTriforceSettings.set("Interface", "OnScreenDisplayMessages", "False")
        else:
            dolphinTriforceSettings.set("Interface", "OnScreenDisplayMessages", "True")

        # Don't confirm at stop
        dolphinTriforceSettings.set("Interface", "ConfirmStop", "False")

        # only 1 window (fixes exit and gui display)
        dolphinTriforceSettings.set("Display", "RenderToMain", "True")
        dolphinTriforceSettings.set("Display", "Fullscreen", "True")

        # Enable Cheats
        dolphinTriforceSettings.set("Core", "EnableCheats", "True")

        # Dual Core
        if system.isOptSet("dual_core") and system.getOptBoolean("dual_core"):
            dolphinTriforceSettings.set("Core", "CPUThread", "True")
        else:
            dolphinTriforceSettings.set("Core", "CPUThread", "False")

        # Gpu Sync
        if system.isOptSet("gpu_sync") and system.getOptBoolean("gpu_sync"):
            dolphinTriforceSettings.set("Core", "SyncGPU", "True")
        else:
            dolphinTriforceSettings.set("Core", "SyncGPU", "False")

        # Language
        dolphinTriforceSettings.set(
            "Core", "SelectedLanguage", str(getGameCubeLangFromEnvironment())
        )  # Wii
        dolphinTriforceSettings.set(
            "Core", "GameCubeLanguage", str(getGameCubeLangFromEnvironment())
        )  # GC

        # Enable MMU
        if system.isOptSet("enable_mmu") and system.getOptBoolean("enable_mmu"):
            dolphinTriforceSettings.set("Core", "MMU", "True")
        else:
            dolphinTriforceSettings.set("Core", "MMU", "False")

        # Backend - Default OpenGL
        dolphinTriforceSettings.set("Core", "GFXBackend", "OGL")

        # Serial Port 1 to AM-Baseband
        # F-Zero GX exception, it needs to not be using the AM-Baseband to function.
        # This cannot be set in the game's INI for some reason.
        if rom == "F-Zero GX (USA).iso":
            dolphinTriforceSettings.set("Core", "SerialPort1", "255")
        else:
            dolphinTriforceSettings.set("Core", "SerialPort1", "6")

        # Gamecube pads forced as AM-Baseband
        # F-Zero GX exception, it needs it to be a regular pad instead.
        if rom == "F-Zero GX (USA).iso":
            dolphinTriforceSettings.set("Core", "SIDevice0", "6")
        else:
            dolphinTriforceSettings.set("Core", "SIDevice0", "11")

        # Save dolphin.ini
        with open(dolphinTriforceConfig.dolphinTriforceIni, "w") as configfile:
            dolphinTriforceSettings.write(configfile)

        ## gfx.ini ##

        dolphinTriforceGFXSettings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        dolphinTriforceGFXSettings.optionxform = lambda optionstr: str(optionstr)
        dolphinTriforceGFXSettings.read(dolphinTriforceConfig.dolphinTriforceGfxIni)

        # Add Default Sections
        if not dolphinTriforceGFXSettings.has_section("Settings"):
            dolphinTriforceGFXSettings.add_section("Settings")
        if not dolphinTriforceGFXSettings.has_section("Hacks"):
            dolphinTriforceGFXSettings.add_section("Hacks")
        if not dolphinTriforceGFXSettings.has_section("Enhancements"):
            dolphinTriforceGFXSettings.add_section("Enhancements")
        if not dolphinTriforceGFXSettings.has_section("Hardware"):
            dolphinTriforceGFXSettings.add_section("Hardware")

        # Graphics setting Aspect Ratio
        if system.isOptSet("dolphin_aspect_ratio"):
            dolphinTriforceGFXSettings.set(
                "Settings", "AspectRatio", system.config["dolphin_aspect_ratio"]
            )
        else:
            # set to zero, which is 'Auto' in Dolphin & REG-Linux
            dolphinTriforceGFXSettings.set("Settings", "AspectRatio", "0")

        # Show fps
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            dolphinTriforceGFXSettings.set("Settings", "ShowFPS", "True")
        else:
            dolphinTriforceGFXSettings.set("Settings", "ShowFPS", "False")

        # HiResTextures
        if system.isOptSet("hires_textures") and system.getOptBoolean("hires_textures"):
            dolphinTriforceGFXSettings.set("Settings", "HiresTextures", "True")
            dolphinTriforceGFXSettings.set("Settings", "CacheHiresTextures", "True")
        else:
            dolphinTriforceGFXSettings.set("Settings", "HiresTextures", "False")
            dolphinTriforceGFXSettings.set("Settings", "CacheHiresTextures", "False")

        # Widescreen Hack
        if system.isOptSet("widescreen_hack") and system.getOptBoolean(
            "widescreen_hack"
        ):
            # Prefer Cheats than Hack
            if system.isOptSet("enable_cheats") and system.getOptBoolean(
                "enable_cheats"
            ):
                dolphinTriforceGFXSettings.set("Settings", "wideScreenHack", "False")
            else:
                dolphinTriforceGFXSettings.set("Settings", "wideScreenHack", "True")
        else:
            dolphinTriforceGFXSettings.set("Settings", "wideScreenHack", "False")

        # Various performance hacks - Default Off
        if system.isOptSet("perf_hacks") and system.getOptBoolean("perf_hacks"):
            dolphinTriforceGFXSettings.set("Hacks", "BBoxEnable", "False")
            dolphinTriforceGFXSettings.set("Hacks", "DeferEFBCopies", "True")
            dolphinTriforceGFXSettings.set("Hacks", "EFBEmulateFormatChanges", "False")
            dolphinTriforceGFXSettings.set("Hacks", "EFBScaledCopy", "True")
            dolphinTriforceGFXSettings.set("Hacks", "EFBToTextureEnable", "True")
            dolphinTriforceGFXSettings.set("Hacks", "SkipDuplicateXFBs", "True")
            dolphinTriforceGFXSettings.set("Hacks", "XFBToTextureEnable", "True")
            dolphinTriforceGFXSettings.set("Enhancements", "ForceFiltering", "True")
            dolphinTriforceGFXSettings.set(
                "Enhancements", "ArbitraryMipmapDetection", "True"
            )
            dolphinTriforceGFXSettings.set("Enhancements", "DisableCopyFilter", "True")
            dolphinTriforceGFXSettings.set("Enhancements", "ForceTrueColor", "True")
        else:
            if dolphinTriforceGFXSettings.has_section("Hacks"):
                dolphinTriforceGFXSettings.remove_option("Hacks", "BBoxEnable")
                dolphinTriforceGFXSettings.remove_option("Hacks", "DeferEFBCopies")
                dolphinTriforceGFXSettings.remove_option(
                    "Hacks", "EFBEmulateFormatChanges"
                )
                dolphinTriforceGFXSettings.remove_option("Hacks", "EFBScaledCopy")
                dolphinTriforceGFXSettings.remove_option("Hacks", "EFBToTextureEnable")
                dolphinTriforceGFXSettings.remove_option("Hacks", "SkipDuplicateXFBs")
                dolphinTriforceGFXSettings.remove_option("Hacks", "XFBToTextureEnable")
            if dolphinTriforceGFXSettings.has_section("Enhancements"):
                dolphinTriforceGFXSettings.remove_option(
                    "Enhancements", "ForceFiltering"
                )
                dolphinTriforceGFXSettings.remove_option(
                    "Enhancements", "ArbitraryMipmapDetection"
                )
                dolphinTriforceGFXSettings.remove_option(
                    "Enhancements", "DisableCopyFilter"
                )
                dolphinTriforceGFXSettings.remove_option(
                    "Enhancements", "ForceTrueColor"
                )

        # Internal resolution settings
        if system.isOptSet("internal_resolution"):
            dolphinTriforceGFXSettings.set(
                "Settings", "EFBScale", system.config["internal_resolution"]
            )
        else:
            dolphinTriforceGFXSettings.set("Settings", "EFBScale", "2")

        # VSync
        if system.isOptSet("vsync"):
            dolphinTriforceGFXSettings.set(
                "Hardware", "VSync", str(system.getOptBoolean("vsync"))
            )
        else:
            dolphinTriforceGFXSettings.set("Hardware", "VSync", "True")

        # Anisotropic filtering
        if system.isOptSet("anisotropic_filtering"):
            dolphinTriforceGFXSettings.set(
                "Enhancements", "MaxAnisotropy", system.config["anisotropic_filtering"]
            )
        else:
            dolphinTriforceGFXSettings.set("Enhancements", "MaxAnisotropy", "0")

        # Anti aliasing
        if system.isOptSet("antialiasing"):
            dolphinTriforceGFXSettings.set(
                "Settings", "MSAA", system.config["antialiasing"]
            )
        else:
            dolphinTriforceGFXSettings.set("Settings", "MSAA", "0")

        # Save gfx.ini
        with open(dolphinTriforceConfig.dolphinTriforceGfxIni, "w") as configfile:
            dolphinTriforceGFXSettings.write(configfile)

        ## logger settings ##

        dolphinTriforceLogSettings = configparser.ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        dolphinTriforceLogSettings.optionxform = lambda optionstr: str(optionstr)
        dolphinTriforceLogSettings.read(dolphinTriforceConfig.dolphinTriforceLoggerIni)

        # Sections
        if not dolphinTriforceLogSettings.has_section("Logs"):
            dolphinTriforceLogSettings.add_section("Logs")

        # Prevent the constant log spam.
        dolphinTriforceLogSettings.set("Logs", "DVD", "False")

        # Save Logger.ini
        with open(dolphinTriforceConfig.dolphinTriforceLoggerIni, "w") as configfile:
            dolphinTriforceLogSettings.write(configfile)

        ## game settings ##

        # These cheat files are required to launch Triforce games, and thus should always be present and enabled.

        game_settings_path = Path(dolphinTriforceConfig.dolphinTriforceGameSettings)
        if not game_settings_path.exists():
            game_settings_path.mkdir(parents=True, exist_ok=True)

        # GFZE01 F-Zero GX (convert to F-Zero AX)

        gfze01_ini_path = game_settings_path / "GFZE01.ini"
        if not gfze01_ini_path.exists():
            with open(gfze01_ini_path, "w") as dolphinTriforceGameSettingsGFZE01:
                dolphinTriforceGameSettingsGFZE01.write("""[Gecko]
$AX
06003F30 00000284
818D831C 280C0000
41820274 3C6C000B
3863FADC 3883000C
38A0000C 4BFFF5F5
3CAC0019 8085D550
64844001 9085D550
3CAC0018 BBC30040
BFC511DC 3C6C0010
A0032A86 280000A4
4082000C 380000A2
B0032A86 380000C0
98035D26 A0A32A7E
3C006000 280500AD
4082000C 3C8C0033
9004DE1C 28050010
408200CC 3C630022
90037B90 3C630003
3800002A B003C754
3800002C B003C758
38000029 B003C778
3800002B B003C77C
3C6C0034 3C006000
9003CE94 3C803C00
60803FA0 9003D000
60803FCC 9003D008
3C809001 608000D0
9003D004 608000D4
9003D00C 3C004800
6000010C 9003D010
3C003CE0 60004323
9003D024 3C0090E1
600000C8 9003D054
3C003800 6000007F
9003D11C 38003F40
B003D122 3C009061
600000EC 9003D124
3C804BFF 6080FEEC
9003D128 6080F9E8
9003D478 380000D7
98035817 3800002C
9803582B 280500AC
40820054 3C8C0032
3C003C60 60008000
90046E44 3C003863
60003F1E 90046E48
3C003806 60000001
90046E54 3C007000
6000FFFE 90046E5C
3C0080ED 60008A9C
90044A64 3C8C0033
3C00809F 600032C0
9004B5D0 280500B0
40820010 3C8C0033
80044E04 900D8A9C
2805009C 40820038
3C6C0032 38000002
98034FBB 9803509B
980351A7 980352DB
980353B3 3800000E
98034FFB 980350DF
980351E7 9803531B
980353F7 3C8C000C
38845404 38640028
38A00018 4BFFF415
38000001 980C0133
3C6CFFF8 3C003800
6000000D 9003FB50
3C808000 80043F24
28000000 4082001C
3C00000B 6000002E
90043F20 3C000039
6000001D 90043F24
3C6C0007 A0043F20
B0030CEE A0043F22
B0030CF6 A0043F24
B0030CFE 38003860
B0030D04 A0043F26
B0030D06 3C6C0009
3C004E80 60000020
90037428 80010014
48016DF4 00000000
0401AFA0 4BFE8F90
[Gecko_Enabled]
$AX
""")
            # GVSJ8P Virtua Striker 2002

        gvsj8p_ini_path = game_settings_path / "GVSJ8P.ini"
        if not gvsj8p_ini_path.exists():
            with open(gvsj8p_ini_path, "w") as dolphinTriforceGameSettingsGVSJ8P:
                dolphinTriforceGameSettingsGVSJ8P.write("""[OnFrame]
$DI Seed Blanker
0x80000000:dword:0x00000000
0x80000004:dword:0x00000000
0x80000008:dword:0x00000000
[OnFrame_Enabled]
$DI Seed Blanker
""")

        # GGPE01 Mario Kart GP 1

        ggpe01_ini_path = game_settings_path / "GGPE01.ini"
        if not ggpe01_ini_path.exists():
            with open(ggpe01_ini_path, "w") as dolphinTriforceGameSettingsGGPE01:
                dolphinTriforceGameSettingsGGPE01.write("""[OnFrame]
$Disable crypto
0x8023D828:dword:0x93A30008
0x8023D82C:dword:0x93C3000C
0x8023D830:dword:0x93E30010
0x8023E088:dword:0x4E800020
$Loop fix
0x800790A0:dword:0x98650025
0x8024F95C:dword:0x60000000
0x80031BF0:dword:0x60000000
0x80031BFC:dword:0x60000000
0x800BE10C:dword:0x4800002C
0x8009F1E0:dword:0x60000000
0x800319D0:dword:0x60000000
[OnFrame_Enabled]
$Disable crypto
$Loop fix
[EmuState]
EmulationIssues = AM-Baseboard
""")

        # GGPE02 Mario Kart GP 2

        ggpe02_ini_path = game_settings_path / "GGPE02.ini"
        if not ggpe02_ini_path.exists():
            with open(ggpe02_ini_path, "w") as dolphinTriforceGameSettingsGGPE02:
                dolphinTriforceGameSettingsGGPE02.write("""[Display]
ProgressiveScan = 0
[Wii]
Widescreen = False
DisableWiimoteSpeaker = 0
[Video]
PH_SZNear = 1
[EmuState]
EmulationStateId = 3
[OnFrame]
$DI Seed Blanker
0x80000000:dword:0x00000000
0x80000004:dword:0x00000000
0x80000008:dword:0x00000000
$DVDInquiry Patchok
0x80286388:dword:0x3C602100
0x8028638C:dword:0x4E800020
$Ignore CMD Encryption
0x80285CD0:dword:0x93A30008
0x80285CD4:dword:0x93C3000C
0x80285CD8:dword:0x93E30010
$Disable CARD
0x80073BF4:dword:0x98650023
0x80073C10:dword:0x98650023
$Disable CAM
0x80073BD8:dword:0x98650025
$Seat Loop patch
0x800BE10C:dword:0x4800002C
$Stuck loop patch
0x8002E100:dword:0x60000000
$60times Loop patch
0x8028B5D4:dword:0x60000000
$GameTestMode Patch
0x8002E340:dword:0x60000000
0x8002E34C:dword:0x60000000
$SeatLoopPatch
0x80084FC4:dword:0x4800000C
0x80085000:dword:0x60000000
$99 credits
0x80690AC0:dword:0x00000063
[OnFrame_Enabled]
$DI Seed Blanker
$DVDInquiry Patchok
$Ignore CMD Encryption
$Disable CARD
$Disable CAM
$Seat Loop patch
$Stuck loop patch
$60times Loop patch
$GameTestMode Patch
$SeatLoopPatch
99 credits
""")

        # # Cheats aren't in key = value format, so the allow_no_value option is needed.
        # dolphinTriforceGameSettingsGGPE01 = configparser.ConfigParser(interpolation=None, allow_no_value=True,delimiters=';')
        # # To prevent ConfigParser from converting to lower case
        # dolphinTriforceGameSettingsGGPE01.optionxform=lambda optionstr: str(optionstr)
        # if os.path.exists(dolphinTriforceConfig.dolphinTriforceGameSettings + "/GGPE01.ini"):
        # dolphinTriforceGameSettingsGGPE01.read(dolphinTriforceConfig.dolphinTriforceGameSettings + "/GGPE01.ini")

        # # GGPE01 sections
        # if not dolphinTriforceGameSettingsGGPE01.has_section("OnFrame"):
        # dolphinTriforceGameSettingsGGPE01.add_section("OnFrame")
        # if not dolphinTriforceGameSettingsGGPE01.has_section("OnFrame_Enabled"):
        # dolphinTriforceGameSettingsGGPE01.add_section("OnFrame_Enabled")

        # # GGPE01 cheats
        # if "$1 credits" not in dolphinTriforceGameSettingsGGPE01["OnFrame"]:
        # dolphinTriforceGameSettingsGGPE01.set("OnFrame", "$1 credits\n0x80690AC0:dword:0x00000001")
        # if "$Emulation Bug Fixes" not in dolphinTriforceGameSettingsGGPE01["OnFrame"]:
        # dolphinTriforceGameSettingsGGPE01.set("OnFrame", "$Emulation Bug Fixes\n0x800319D0:dword:0x60000000\n0x80031BF0:dword:0x60000000\n0x80031BFC:dword::0x60000000\n0x800BE10C:dword:0x4800002C\n0x800790A0:dword:0x98650025")
        # if "$1 credits" not in dolphinTriforceGameSettingsGGPE01["OnFrame_Enabled"]:
        # dolphinTriforceGameSettingsGGPE01.set("OnFrame_Enabled", "$1 credits")
        # if "$Emulation Bug Fixes" not in dolphinTriforceGameSettingsGGPE01["OnFrame_Enabled"]:
        # dolphinTriforceGameSettingsGGPE01.set("OnFrame_Enabled", "$Emulation Bug Fixes")

        # # Save GGPE01.ini
        # with open(dolphinTriforceConfig.dolphinTriforceGameSettings + "/GGPE01.ini", 'w') as configfile:
        # dolphinTriforceGameSettingsGGPE01.write(configfile)

        command_array = [
            "dolphin-triforce",
            "-b",
            "-u",
            str(Path("/userdata/system/configs/dolphin-triforce")),
            "-e",
            rom,
        ]
        if system.isOptSet("platform"):
            command_array = [
                "dolphin-triforce-nogui",
                "-b",
                "-u",
                str(Path("/userdata/system/configs/dolphin-triforce")),
                "-p",
                system.config["platform"],
                "-e",
                rom,
            ]

        return Command(array=command_array)

    def get_in_game_ratio(
        self, config: Any, game_resolution: dict[str, int], rom: str
    ) -> float:
        if "dolphin_aspect_ratio" in config and (
            config["dolphin_aspect_ratio"] == "1"
            or config["dolphin_aspect_ratio"] == "3"
            and (
                game_resolution["width"] / float(game_resolution["height"])
                > ((16.0 / 9.0) - 0.1)
            )
        ):
            return 16 / 9
        return 4 / 3


# Seem to be only for the gamecube. However, while this is not in a gamecube section
# It may be used for something else, so set it anyway
def getGameCubeLangFromEnvironment():
    lang = environ["LANG"][:5]
    availableLanguages = {
        "en_US": 0,
        "de_DE": 1,
        "fr_FR": 2,
        "es_ES": 3,
        "it_IT": 4,
        "nl_NL": 5,
    }
    if lang in availableLanguages:
        return availableLanguages[lang]
    return availableLanguages["en_US"]
