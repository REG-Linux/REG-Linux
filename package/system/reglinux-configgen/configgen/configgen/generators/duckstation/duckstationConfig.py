from os import environ
from pathlib import Path
from typing import Any

from configgen.systemFiles import BIOS, CHEATS, CONF, ROMS, SAVES, SCREENSHOTS

DUCKSTATION_CONFIG_PATH = CONF / "duckstation" / "settings.ini"
DUCKSTATION_SAVES_DIR = SAVES / "duckstation"
DUCKSTATION_CHEATS_DIR = CHEATS / "duckstation"
DUCKSTATION_MEMORY_CARDS_DIR = SAVES / "duckstation" / "memcards"
DUCKSTATION_ROMS_DIR = ROMS / "psx"
DUCKSTATION_CACHE_DIR = Path("/userdata/system/cache/duckstation")
DUCKSTATION_BIN_PATH = Path("/usr/duckstation/DuckStation.AppImage")
DUCKSTATION_NOGUI_PATH = Path("/usr/bin/duckstation-nogui")


def setDuckstationConfig(
    duckstatonConfig: Any, system: Any, playersControllers: Any,
) -> None:
    ## [Main]
    if not duckstatonConfig.has_section("Main"):
        duckstatonConfig.add_section("Main")
    # Settings, Language and ConfirmPowerOff
    duckstatonConfig.set(
        "Main", "SettingsVersion", "3",
    )  # Probably to be updated in the future
    duckstatonConfig.set("Main", "InhibitScreensaver", "true")
    duckstatonConfig.set("Main", "StartPaused", "false")
    # Force Fullscreen
    duckstatonConfig.set("Main", "StartFullscreen", "true")
    duckstatonConfig.set("Main", "PauseOnFocusLoss", "false")
    duckstatonConfig.set("Main", "PauseOnMenu", "true")
    duckstatonConfig.set("Main", "ConfirmPowerOff", "false")
    # Force applying game Settings fixes
    duckstatonConfig.set("Main", "ApplyGameSettings", "true")
    # Remove wizard
    duckstatonConfig.set("Main", "SetupWizardIncomplete", "false")
    # overclock
    if system.isOptSet("duckstation_clocking"):
        duckstatonConfig.set(
            "Main", "EmulationSpeed", system.config["duckstation_clocking"],
        )
    else:
        duckstatonConfig.set("Main", "EmulationSpeed", "1")
    # host refresh rate
    if system.isOptSet("duckstation_hrr"):
        duckstatonConfig.set(
            "Main", "SyncToHostRefreshRate", system.config["duckstation_hrr"],
        )
    else:
        duckstatonConfig.set("Main", "SyncToHostRefreshRate", "false")

    # Rewind
    # if system.isOptSet('rewind') and system.getOptBoolean('rewind') == True:
    duckstatonConfig.set("Main", "RewindEnable", "true")
    duckstatonConfig.set("Main", "RewindFrequency", "1")  # Frame skipped each seconds
    if (
        system.isOptSet("duckstation_rewind")
        and system.config["duckstation_rewind"] == "120"
    ):
        duckstatonConfig.set(
            "Main", "RewindSaveSlots", "120",
        )  # Total duration available in sec
    elif (
        system.isOptSet("duckstation_rewind")
        and system.config["duckstation_rewind"] == "90"
    ):
        duckstatonConfig.set("Main", "RewindSaveSlots", "90")
    elif (
        system.isOptSet("duckstation_rewind")
        and system.config["duckstation_rewind"] == "60"
    ):
        duckstatonConfig.set("Main", "RewindSaveSlots", "60")
    elif (
        system.isOptSet("duckstation_rewind")
        and system.config["duckstation_rewind"] == "30"
    ):
        duckstatonConfig.set("Main", "RewindSaveSlots", "30")
    elif (
        system.isOptSet("duckstation_rewind")
        and system.config["duckstation_rewind"] == "15"
    ):
        duckstatonConfig.set("Main", "RewindSaveSlots", "15")
    elif (
        system.isOptSet("duckstation_rewind")
        and system.config["duckstation_rewind"] == "10"
    ):
        duckstatonConfig.set("Main", "RewindSaveSlots", "100")
        duckstatonConfig.set("Main", "RewindFrequency", "0.100000")
    elif (
        system.isOptSet("duckstation_rewind")
        and system.config["duckstation_rewind"] == "5"
    ):
        duckstatonConfig.set("Main", "RewindSaveSlots", "50")
        duckstatonConfig.set("Main", "RewindFrequency", "0.050000")
    else:
        duckstatonConfig.set("Main", "RewindEnable", "false")
    # Discord
    duckstatonConfig.set("Main", "EnableDiscordPresence", "false")
    # Language
    duckstatonConfig.set("Main", "Language", getLangFromEnvironment())

    ## [Console]
    if not duckstatonConfig.has_section("Console"):
        duckstatonConfig.add_section("Console")
    # Region
    if system.isOptSet("duckstation_region"):
        duckstatonConfig.set("Console", "Region", system.config["duckstation_region"])
    else:
        duckstatonConfig.set("Console", "Region", "Auto")

    ## [BIOS]
    if not duckstatonConfig.has_section("BIOS"):
        duckstatonConfig.add_section("BIOS")
    duckstatonConfig.set("BIOS", "SearchDirectory", str(BIOS))
    # Boot Logo
    if system.isOptSet("duckstation_PatchFastBoot"):
        duckstatonConfig.set(
            "BIOS", "PatchFastBoot", system.config["duckstation_PatchFastBoot"],
        )
    else:
        duckstatonConfig.set("BIOS", "PatchFastBoot", "false")
    # Find & populate BIOS
    USbios = [
        "scph101.bin",
        "scph1001.bin",
        "scph5501.bin",
        "scph7001.bin",
        "scph7501.bin",
    ]
    EUbios = [
        "scph1002.bin",
        "scph5502.bin",
        "scph5552.bin",
        "scph7002.bin",
        "scph7502.bin",
        "scph9002.bin",
        "scph102a.bin",
        "scph102b.bin",
    ]
    JPbios = [
        "scph100.bin",
        "scph1000.bin",
        "scph3000.bin",
        "scph3500.bin",
        "scph5500.bin",
        "scph7000.bin",
        "scph7003.bin",
    ]
    biosFound = False
    USbiosFile = EUbiosFile = JPbiosFile = None
    for bio in USbios:
        if (BIOS / bio).exists():
            USbiosFile = bio
            biosFound = True
            break
    for bio in EUbios:
        if (BIOS / bio).exists():
            EUbiosFile = bio
            biosFound = True
            break
    for bio in JPbios:
        if (BIOS / bio).exists():
            JPbiosFile = bio
            biosFound = True
            break
    if not biosFound:
        raise Exception("No PSX1 BIOS found")
    if USbiosFile is not None:
        duckstatonConfig.set("BIOS", "PathNTSCU", USbiosFile)
    if EUbiosFile is not None:
        duckstatonConfig.set("BIOS", "PathPAL", EUbiosFile)
    if JPbiosFile is not None:
        duckstatonConfig.set("BIOS", "PathNTSCJ", JPbiosFile)

    ## [CPU]
    if not duckstatonConfig.has_section("CPU"):
        duckstatonConfig.add_section("CPU")
    # ExecutionMode
    if system.isOptSet("duckstation_executionmode"):
        duckstatonConfig.set(
            "CPU", "ExecutionMode", system.config["duckstation_executionmode"],
        )
    else:
        duckstatonConfig.set("CPU", "ExecutionMode", "Recompiler")

    ## [GPU]
    if not duckstatonConfig.has_section("GPU"):
        duckstatonConfig.add_section("GPU")
    # Renderer
    if system.isOptSet("duckstation_gfxbackend"):
        duckstatonConfig.set("GPU", "Renderer", system.config["duckstation_gfxbackend"])
    else:
        duckstatonConfig.set("GPU", "Renderer", "OpenGL")
    # Multisampling force (MSAA or SSAA) - no GUI option anymore...
    duckstatonConfig.set("GPU", "PerSampleShading", "false")
    duckstatonConfig.set("GPU", "Multisamples", "1")
    # Threaded Presentation (Vulkan Improve)
    if system.isOptSet("duckstation_threadedpresentation"):
        duckstatonConfig.set(
            "GPU",
            "ThreadedPresentation",
            system.config["duckstation_threadedpresentation"],
        )
    else:
        duckstatonConfig.set("GPU", "ThreadedPresentation", "false")
    # Internal resolution
    if system.isOptSet("duckstation_resolution_scale"):
        duckstatonConfig.set(
            "GPU", "ResolutionScale", system.config["duckstation_resolution_scale"],
        )
    else:
        duckstatonConfig.set("GPU", "ResolutionScale", "1")
    # WideScreen Hack
    if system.isOptSet("duckstation_widescreen_hack"):
        duckstatonConfig.set(
            "GPU", "WidescreenHack", system.config["duckstation_widescreen_hack"],
        )
    else:
        duckstatonConfig.set("GPU", "WidescreenHack", "false")
    # Force 60hz
    if system.isOptSet("duckstation_60hz"):
        duckstatonConfig.set(
            "GPU", "ForceNTSCTimings", system.config["duckstation_60hz"],
        )
    else:
        duckstatonConfig.set("GPU", "ForceNTSCTimings", "false")
    # TextureFiltering
    if (
        system.isOptSet("duckstation_texture_filtering")
        and system.config["duckstation_texture_filtering"] != "Nearest"
    ):
        duckstatonConfig.set(
            "GPU", "TextureFilter", system.config["duckstation_texture_filtering"],
        )
    else:
        duckstatonConfig.set("GPU", "TextureFilter", "Nearest")
    # PGXP - enabled by default
    if system.isOptSet("duckstation_pgxp"):
        duckstatonConfig.set("GPU", "PGXPEnable", system.config["duckstation_pgxp"])
        duckstatonConfig.set("GPU", "PGXPCulling", system.config["duckstation_pgxp"])
        duckstatonConfig.set(
            "GPU", "PGXPTextureCorrection", system.config["duckstation_pgxp"],
        )
        duckstatonConfig.set(
            "GPU", "PGXPPreserveProjFP", system.config["duckstation_pgxp"],
        )
    else:
        duckstatonConfig.set("GPU", "PGXPEnable", "true")
        duckstatonConfig.set("GPU", "PGXPCulling", "true")
        duckstatonConfig.set("GPU", "PGXPTextureCorrection", "true")
        duckstatonConfig.set("GPU", "PGXPPreserveProjFP", "true")
    # True Color
    if system.isOptSet("duckstation_truecolour"):
        duckstatonConfig.set(
            "GPU", "TrueColor", system.config["duckstation_truecolour"],
        )
    else:
        duckstatonConfig.set("GPU", "TrueColor", "false")
    # Scaled Dithering
    if system.isOptSet("duckstation_dithering"):
        duckstatonConfig.set(
            "GPU", "ScaledDithering", system.config["duckstation_dithering"],
        )
    else:
        duckstatonConfig.set("GPU", "ScaledDithering", "true")
    # Disable Interlacing
    if system.isOptSet("duckstation_interlacing"):
        duckstatonConfig.set(
            "GPU", "DisableInterlacing", system.config["duckstation_interlacing"],
        )
    else:
        duckstatonConfig.set("GPU", "DisableInterlacing", "false")
    # Anti-Aliasing
    if system.isOptSet("duckstation_antialiasing"):
        if "ssaa" in system.config["duckstation_antialiasing"]:
            duckstatonConfig.set("GPU", "PerSampleShading", "true")
            parts = system.config["duckstation_antialiasing"].split("-")
            multisamples = parts[0]
            duckstatonConfig.set("GPU", "Multisamples", multisamples)
        else:
            duckstatonConfig.set(
                "GPU", "Multisamples", system.config["duckstation_antialiasing"],
            )
            duckstatonConfig.set("GPU", "PerSampleShading", "false")

    ## [Display]
    if not duckstatonConfig.has_section("Display"):
        duckstatonConfig.add_section("Display")
    # Aspect Ratio
    if system.isOptSet("duckstation_ratio"):
        duckstatonConfig.set(
            "Display", "AspectRatio", system.config["duckstation_ratio"],
        )
        if system.config["duckstation_ratio"] != "4:3":
            system.config["bezel"] = "none"
    else:
        duckstatonConfig.set("Display", "AspectRatio", "Auto (Game Native)")
    # Vsync
    if system.isOptSet("duckstation_vsync"):
        duckstatonConfig.set("Display", "VSync", system.config["duckstation_vsync"])
    else:
        duckstatonConfig.set("Display", "VSync", "false")
    # CropMode
    if system.isOptSet("duckstation_CropMode"):
        duckstatonConfig.set(
            "Display", "CropMode", system.config["duckstation_CropMode"],
        )
    else:
        duckstatonConfig.set("Display", "CropMode", "Overscan")
    # Enable Frameskipping = option missing
    duckstatonConfig.set("Display", "DisplayAllFrames", "false")
    # OSD Messages
    if system.isOptSet("duckstation_osd"):
        duckstatonConfig.set(
            "Display", "ShowOSDMessages", system.config["duckstation_osd"],
        )
    else:
        duckstatonConfig.set("Display", "ShowOSDMessages", "false")
    # Optimal frame pacing
    if system.isOptSet("duckstation_ofp"):
        duckstatonConfig.set(
            "Display", "DisplayAllFrames", system.config["duckstation_ofp"],
        )
    else:
        duckstatonConfig.set("Display", "DisplayAllFrames", "false")
    # Integer Scaling
    if system.isOptSet("duckstation_integer"):
        duckstatonConfig.set(
            "Display", "IntegerScaling", system.config["duckstation_integer"],
        )
    else:
        duckstatonConfig.set("Display", "IntegerScaling", "false")
    # Linear Filtering
    if system.isOptSet("duckstation_linear"):
        duckstatonConfig.set(
            "Display", "LinearFiltering", system.config["duckstation_linear"],
        )
    else:
        duckstatonConfig.set("Display", "LinearFiltering", "false")
    # Stretch
    if (
        system.isOptSet("duckstation_stretch")
        and system.config["duckstation_stretch"] == "true"
    ):
        duckstatonConfig.set("Display", "Stretch", system.config["duckstation_stretch"])
        if (
            not system.isOptSet("duckstation_integer")
            or system.config["duckstation_integer"] == "false"
        ):
            system.config["bezel"] = "none"
    else:
        duckstatonConfig.set("Display", "Stretch", "false")

    ## [Audio]
    if not duckstatonConfig.has_section("Audio"):
        duckstatonConfig.add_section("Audio")
    if system.isOptSet("duckstation_audio_mode"):
        duckstatonConfig.set(
            "Audio", "StretchMode", system.config["duckstation_audio_mode"],
        )
    else:
        duckstatonConfig.set("Audio", "StretchMode", "TimeStretch")

    ## [GameList]
    if not duckstatonConfig.has_section("GameList"):
        duckstatonConfig.add_section("GameList")
    duckstatonConfig.set("GameList", "RecursivePaths", str(DUCKSTATION_ROMS_DIR))

    ## [Cheevos]
    if not duckstatonConfig.has_section("Cheevos"):
        duckstatonConfig.add_section("Cheevos")
    # RetroAchievements
    if system.isOptSet("retroachievements") and system.getOptBoolean(
        "retroachievements",
    ):
        username = system.config.get("retroachievements.username", "")
        hardcore = system.config.get("retroachievements.hardcore", "")
        presence = system.config.get("retroachievements.richpresence", "")
        indicator = system.config.get("retroachievements.challenge_indicators", "")
        leaderbd = system.config.get("retroachievements.leaderboards", "")
        token = system.config.get("retroachievements.token", "")
        duckstatonConfig.set("Cheevos", "Enabled", "true")
        duckstatonConfig.set("Cheevos", "Username", username)
        duckstatonConfig.set("Cheevos", "Token", token)
        if hardcore == "1":
            duckstatonConfig.set(
                "Cheevos", "ChallengeMode", "true",
            )  # For "hardcore" retroachievement points (no save, no rewind...)
        else:
            duckstatonConfig.set("Cheevos", "ChallengeMode", "false")
        if presence == "1":
            duckstatonConfig.set(
                "Cheevos", "RichPresence", "true",
            )  # Enable rich presence information will be collected and sent to the server where supported
        else:
            duckstatonConfig.set("Cheevos", "RichPresence", "false")
        if indicator == "1":
            duckstatonConfig.set("Cheevos", "PrimedIndicators", "true")
        else:
            duckstatonConfig.set("Cheevos", "PrimedIndicators", "false")
        if leaderbd == "1":
            duckstatonConfig.set("Cheevos", "Leaderboards", "true")
        else:
            duckstatonConfig.set("Cheevos", "Leaderboards", "false")
        # duckstatonConfig.set("Cheevos", "UseFirstDiscFromPlaylist", "false") # When enabled, the first disc in a playlist will be used for achievements, regardless of which disc is active
        # duckstatonConfig.set("Cheevos", "TestMode",      "false")            # DuckStation will assume all achievements are locked and not send any unlock notifications to the server.
    else:
        duckstatonConfig.set("Cheevos", "Enabled", "false")

    ## [TextureReplacements]
    if not duckstatonConfig.has_section("TextureReplacements"):
        duckstatonConfig.add_section("TextureReplacements")
    # Texture Replacement saves\textures\psx game id - by default in Normal
    if (
        system.isOptSet("duckstation_custom_textures")
        and system.config["duckstation_custom_textures"] == "0"
    ):
        duckstatonConfig.set(
            "TextureReplacements", "EnableVRAMWriteReplacements", "false",
        )
        duckstatonConfig.set("TextureReplacements", "PreloadTextures", "false")
    elif (
        system.isOptSet("duckstation_custom_textures")
        and system.config["duckstation_custom_textures"] == "preload"
    ):
        duckstatonConfig.set(
            "TextureReplacements", "EnableVRAMWriteReplacements", "true",
        )
        duckstatonConfig.set("TextureReplacements", "PreloadTextures", "true")
    else:
        duckstatonConfig.set(
            "TextureReplacements", "EnableVRAMWriteReplacements", "true",
        )
        duckstatonConfig.set("TextureReplacements", "PreloadTextures", "false")

    ## [MemoryCards]
    if not duckstatonConfig.has_section("MemoryCards"):
        duckstatonConfig.add_section("MemoryCards")
    # Set memory card location
    duckstatonConfig.set("MemoryCards", "Directory", str(DUCKSTATION_MEMORY_CARDS_DIR))

    ## [Folders]
    if not duckstatonConfig.has_section("Folders"):
        duckstatonConfig.add_section("Folders")
    # Set other folder locations too
    duckstatonConfig.set("Folders", "Cache", str(DUCKSTATION_CACHE_DIR))
    duckstatonConfig.set("Folders", "Screenshots", str(SCREENSHOTS))
    duckstatonConfig.set("Folders", "SaveStates", str(DUCKSTATION_SAVES_DIR))
    duckstatonConfig.set("Folders", "Cheats", str(DUCKSTATION_CHEATS_DIR))

    ## [CDROM]
    if not duckstatonConfig.has_section("CDROM"):
        duckstatonConfig.add_section("CDROM")
    if system.isOptSet("duckstation_boot_without_sbi"):
        duckstatonConfig.set(
            "CDROM",
            "AllowBootingWithoutSBIFile",
            system.config["duckstation_boot_without_sbi"],
        )
    else:
        duckstatonConfig.set("CDROM", "AllowBootingWithoutSBIFile", "false")

    # Auto Updates
    if not duckstatonConfig.has_section("AutoUpdater"):
        duckstatonConfig.add_section("AutoUpdater")
        # Set auto update
        duckstatonConfig.set("AutoUpdater", "CheckAtStartup", "false")


def getLangFromEnvironment():
    lang = environ["LANG"][:5]
    availableLanguages = {
        "en_US": "en",
        "de_DE": "de",
        "fr_FR": "fr",
        "es_ES": "es",
        "he_IL": "he",
        "it_IT": "it",
        "ja_JP": "ja",
        "nl_NL": "nl",
        "pl_PL": "pl",
        "pt_BR": "pt-br",
        "pt_PT": "pt-pt",
        "ru_RU": "ru",
        "zh_CN": "zh-cn",
    }
    if lang in availableLanguages:
        return availableLanguages[lang]
    return availableLanguages["en_US"]
