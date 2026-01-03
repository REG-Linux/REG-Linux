from configparser import ConfigParser
from contextlib import suppress
from os import environ
from pathlib import Path
from subprocess import CalledProcessError, check_output
from typing import Any

from configgen.Command import Command
from configgen.controllers import gunsNeedCrosses
from configgen.generators.Generator import Generator
from configgen.utils.logger import get_logger

from .dolphinConfig import (
    DOLPHIN_BIN_PATH,
    DOLPHIN_CONFIG_PATH,
    DOLPHIN_GFX_PATH,
    DOLPHIN_SAVES_DIR,
    DOLPHIN_SYSCONF_PATH,
    getRatioFromConfig,
    updateConfig,
)
from .dolphinControllers import generateControllerConfig

eslog = get_logger(__name__)


class DolphinGenerator(Generator):
    # this emulator/core requires X server to run
    # TODO I think this is wrong and it can runs on wayland...
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
        """Generate the Dolphin emulator configuration.

        Args:
            system: System configuration object
            rom: ROM file path
            players_controllers: Player controllers configuration
            metadata: Game metadata
            guns: Light gun controllers
            wheels: Wheel controllers
            game_resolution: Game resolution dictionary

        Returns:
            Command object to execute the emulator

        """
        config_dir = Path(DOLPHIN_CONFIG_PATH).parent
        if not config_dir.exists():
            config_dir.mkdir(parents=True, exist_ok=True)

        # Dir required for saves
        saves_dir = Path(DOLPHIN_SAVES_DIR) / "StateSaves"
        if not saves_dir.exists():
            saves_dir.mkdir(parents=True, exist_ok=True)

        # FIXME Generate the controller config(s)
        generateControllerConfig(
            system, players_controllers, metadata, wheels, rom, guns,
        )

        # [dolphin.ini]
        dolphin_settings = ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        dolphin_settings.optionxform = lambda optionstr: str(optionstr)
        config_path = Path(DOLPHIN_CONFIG_PATH)
        if config_path.exists():
            dolphin_settings.read(DOLPHIN_CONFIG_PATH)

        # Sections
        if not dolphin_settings.has_section("General"):
            dolphin_settings.add_section("General")
        if not dolphin_settings.has_section("Core"):
            dolphin_settings.add_section("Core")
        if not dolphin_settings.has_section("DSP"):
            dolphin_settings.add_section("DSP")
        if not dolphin_settings.has_section("Interface"):
            dolphin_settings.add_section("Interface")
        if not dolphin_settings.has_section("Analytics"):
            dolphin_settings.add_section("Analytics")
        if not dolphin_settings.has_section("Display"):
            dolphin_settings.add_section("Display")
        if not dolphin_settings.has_section("GBA"):
            dolphin_settings.add_section("GBA")

        # Define default games path
        if "ISOPaths" not in dolphin_settings["General"]:
            dolphin_settings.set("General", "ISOPath0", str(Path("/userdata/roms/wii")))
            dolphin_settings.set(
                "General", "ISOPath1", str(Path("/userdata/roms/gamecube")),
            )
            dolphin_settings.set("General", "ISOPaths", "2")

        # Don't ask about statistics
        dolphin_settings.set("Analytics", "PermissionAsked", "True")

        # PanicHandlers displaymessages
        dolphin_settings.set("Interface", "UsePanicHandlers", "False")

        # Display message in game (Memory card save and many more...)
        if system.isOptSet("ShowDpMsg") and system.getOptBoolean("ShowDpMsg"):
            dolphin_settings.set("Interface", "OnScreenDisplayMessages", "True")
        else:
            dolphin_settings.set("Interface", "OnScreenDisplayMessages", "False")

        # Don't confirm at stop
        dolphin_settings.set("Interface", "ConfirmStop", "False")

        # fixes exit and gui display
        dolphin_settings.remove_option("Display", "RenderToMain")
        dolphin_settings.remove_option("Display", "Fullscreen")

        # Enable Cheats
        if system.isOptSet("enable_cheats") and system.getOptBoolean("enable_cheats"):
            dolphin_settings.set("Core", "EnableCheats", "True")
        else:
            dolphin_settings.set("Core", "EnableCheats", "False")

        # Speed up disc transfer rate
        if system.isOptSet("enable_fastdisc") and system.getOptBoolean(
            "enable_fastdisc",
        ):
            dolphin_settings.set("Core", "FastDiscSpeed", "True")
        else:
            dolphin_settings.set("Core", "FastDiscSpeed", "False")

        # Dual Core
        if system.isOptSet("dual_core") and system.getOptBoolean("dual_core"):
            dolphin_settings.set("Core", "CPUThread", "True")
        else:
            dolphin_settings.set("Core", "CPUThread", "False")

        # Gpu Sync
        if system.isOptSet("gpu_sync") and system.getOptBoolean("gpu_sync"):
            dolphin_settings.set("Core", "SyncGPU", "True")
        else:
            dolphin_settings.set("Core", "SyncGPU", "False")

        # Gamecube Language
        if system.isOptSet("gamecube_language"):
            dolphin_settings.set(
                "Core", "SelectedLanguage", system.config["gamecube_language"],
            )
        else:
            dolphin_settings.set(
                "Core", "SelectedLanguage", str(getGameCubeLangFromEnvironment()),
            )

        # Enable MMU
        if system.isOptSet("enable_mmu") and system.getOptBoolean("enable_mmu"):
            dolphin_settings.set("Core", "MMU", "True")
        else:
            dolphin_settings.set("Core", "MMU", "False")

        # Backend - Default OpenGL
        if system.isOptSet("gfxbackend") and system.config["gfxbackend"] == "Vulkan":
            dolphin_settings.set("Core", "GFXBackend", "Vulkan")
            # Check Vulkan
            try:
                have_vulkan = check_output(
                    ["/usr/bin/system-vulkan", "hasVulkan"], text=True,
                ).strip()
                if have_vulkan != "true":
                    eslog.debug(
                        "Vulkan driver is not available on the system. Using OpenGL instead.",
                    )
                    dolphin_settings.set("Core", "GFXBackend", "OGL")
            except CalledProcessError:
                eslog.debug("Error checking for discrete GPU.")
        else:
            dolphin_settings.set("Core", "GFXBackend", "OGL")

        # Wiimote scanning
        dolphin_settings.set("Core", "WiimoteContinuousScanning", "True")

        # Gamecube ports
        # Create a for loop going 1 through to 4 and iterate through it:
        for i in range(1, 5):
            key = "dolphin_port_" + str(i) + "_type"
            if system.isOptSet(key):
                value = system.config[key]
                # Set value to 6 if it is 6a or 6b. This is to differentiate between Standard Controller and GameCube Controller type.
                value = "6" if value in ["6a", "6b"] else value
                # Sub in the appropriate values from es_features, accounting for the 1 integer difference.
                dolphin_settings.set("Core", "SIDevice" + str(i - 1), value)
            # if the pad is a wheel and on gamecube, use it
            elif (
                system.name == "gamecube"
                and system.isOptSet("use_wheels")
                and system.getOptBoolean("use_wheels")
                and len(wheels) > 0
                and str(i) in players_controllers
                and players_controllers[str(i)].dev in wheels
            ):
                dolphin_settings.set("Core", "SIDevice" + str(i - 1), "8")
            else:
                dolphin_settings.set("Core", "SIDevice" + str(i - 1), "6")

        # HiResTextures for guns part 1/2 (see below the part 2)
        if (
            system.isOptSet("use_guns")
            and system.getOptBoolean("use_guns")
            and len(guns) > 0
            and (
                (
                    not system.isOptSet("dolphin-lightgun-hide-crosshair")
                    and not gunsNeedCrosses(guns)
                )
                or system.getOptBoolean("dolphin-lightgun-hide-crosshair")
            )
        ):
            dolphin_settings.set(
                "General",
                "CustomTexturesPath",
                str(Path("/usr/share/DolphinCrosshairsPack")),
            )
        else:
            dolphin_settings.remove_option("General", "CustomTexturesPath")

        # Change discs automatically
        dolphin_settings.set("Core", "AutoDiscChange", "True")

        # Skip Menu
        if system.isOptSet("dolphin_SkipIPL") and system.getOptBoolean(
            "dolphin_SkipIPL",
        ):
            # check files exist to avoid crashes
            ipl_regions = ["USA", "EUR", "JAP"]
            base_path = Path("/userdata/bios/GC")
            if any((base_path / region / "IPL.bin").exists() for region in ipl_regions):
                dolphin_settings.set("Core", "SkipIPL", "False")
            else:
                dolphin_settings.set("Core", "SkipIPL", "True")
        else:
            dolphin_settings.set("Core", "SkipIPL", "True")

        # Set audio backend
        dolphin_settings.set("DSP", "Backend", "Cubeb")

        # Dolby Pro Logic II for surround sound
        # DPL II requires DSPHLE to be disabled
        if system.isOptSet("dplii") and system.getOptBoolean("dplii"):
            dolphin_settings.set("Core", "DPL2Decoder", "True")
            dolphin_settings.set("Core", "DSPHLE", "False")
            dolphin_settings.set("DSP", "EnableJIT", "True")
        else:
            dolphin_settings.set("Core", "DPL2Decoder", "False")
            dolphin_settings.set("Core", "DSPHLE", "True")
            dolphin_settings.set("DSP", "EnableJIT", "False")

        # Save dolphin.ini
        with open(DOLPHIN_CONFIG_PATH, "w") as configfile:
            dolphin_settings.write(configfile)

        # [gfx.ini]
        dolphin_gfx_settings = ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        dolphin_gfx_settings.optionxform = lambda optionstr: str(optionstr)
        dolphin_gfx_settings.read(DOLPHIN_GFX_PATH)

        # Add Default Sections
        if not dolphin_gfx_settings.has_section("Settings"):
            dolphin_gfx_settings.add_section("Settings")
        if not dolphin_gfx_settings.has_section("Hacks"):
            dolphin_gfx_settings.add_section("Hacks")
        if not dolphin_gfx_settings.has_section("Enhancements"):
            dolphin_gfx_settings.add_section("Enhancements")
        if not dolphin_gfx_settings.has_section("Hardware"):
            dolphin_gfx_settings.add_section("Hardware")

        # Set Vulkan adapter
        try:
            have_vulkan = check_output(
                ["/usr/bin/system-vulkan", "hasVulkan"], text=True,
            ).strip()
            if have_vulkan == "true":
                eslog.debug("Vulkan driver is available on the system.")
                try:
                    have_discrete = check_output(
                        ["/usr/bin/system-vulkan", "hasDiscrete"], text=True,
                    ).strip()
                    if have_discrete == "true":
                        eslog.debug(
                            "A discrete GPU is available on the system. We will use that for performance",
                        )
                        try:
                            discrete_index = check_output(
                                ["/usr/bin/system-vulkan", "discreteIndex"], text=True,
                            ).strip()
                            if discrete_index != "":
                                eslog.debug(
                                    f"Using Discrete GPU Index: {discrete_index} for Dolphin",
                                )
                                dolphin_gfx_settings.set(
                                    "Hardware", "Adapter", discrete_index,
                                )
                            else:
                                eslog.debug("Couldn't get discrete GPU index")
                        except CalledProcessError:
                            eslog.debug("Error getting discrete GPU index")
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
                                integrated_index = check_output(
                                    ["/usr/bin/system-vulkan", "integratedIndex"],
                                    text=True,
                                ).strip()
                                if integrated_index != "":
                                    eslog.debug(
                                        f"Using Integrated GPU Index: {integrated_index} for Dolphin",
                                    )
                                    dolphin_gfx_settings.set(
                                        "Hardware", "Adapter", integrated_index,
                                    )
                                else:
                                    eslog.debug("Couldn't get integrated GPU index")
                            except CalledProcessError:
                                eslog.debug("Error getting integrated GPU index")
                        else:
                            eslog.debug(
                                "Integrated GPU is not available on the system. Cannot enable Vulkan.",
                            )
                except CalledProcessError:
                    eslog.debug("Error checking for discrete GPU.")
        except CalledProcessError:
            eslog.debug("Error executing system-vulkan script.")

        # Graphics setting Aspect Ratio
        if system.isOptSet("dolphin_aspect_ratio"):
            dolphin_gfx_settings.set(
                "Settings", "AspectRatio", system.config["dolphin_aspect_ratio"],
            )
        else:
            # set to zero, which is 'Auto' in Dolphin & REG-Linux
            dolphin_gfx_settings.set("Settings", "AspectRatio", "0")

        # Show fps
        if system.isOptSet("showFPS") and system.getOptBoolean("showFPS"):
            dolphin_gfx_settings.set("Settings", "ShowFPS", "True")
        else:
            dolphin_gfx_settings.set("Settings", "ShowFPS", "False")

        # HiResTextures
        if system.isOptSet("hires_textures") and system.getOptBoolean("hires_textures"):
            dolphin_gfx_settings.set("Settings", "HiresTextures", "True")
            dolphin_gfx_settings.set("Settings", "CacheHiresTextures", "True")
        else:
            dolphin_gfx_settings.set("Settings", "HiresTextures", "False")
            dolphin_gfx_settings.set("Settings", "CacheHiresTextures", "False")

        # HiResTextures for guns part 2/2 (see upper part1)
        if (
            system.isOptSet("use_guns")
            and system.getOptBoolean("use_guns")
            and len(guns) > 0
            and (
                not system.isOptSet("dolphin-lightgun-hide-crosshair")
                or system.getOptBoolean("dolphin-lightgun-hide-crosshair")
            )
        ):
            # erase what can be set by the option hires_textures
            dolphin_gfx_settings.set("Settings", "HiresTextures", "True")
            dolphin_gfx_settings.set("Settings", "CacheHiresTextures", "True")

        # Widescreen Hack
        if system.isOptSet("widescreen_hack") and system.getOptBoolean(
            "widescreen_hack",
        ):
            # Prefer Cheats than Hack
            if system.isOptSet("enable_cheats") and system.getOptBoolean(
                "enable_cheats",
            ):
                dolphin_gfx_settings.set("Settings", "wideScreenHack", "False")
            else:
                dolphin_gfx_settings.set("Settings", "wideScreenHack", "True")
        else:
            dolphin_gfx_settings.set("Settings", "wideScreenHack", "False")

        # Ubershaders (synchronous_ubershader by default)
        if (
            system.isOptSet("ubershaders")
            and system.config["ubershaders"] != "no_ubershader"
        ):
            dolphin_gfx_settings.set(
                "Settings", "ShaderCompilationMode", system.config["ubershaders"],
            )
        else:
            dolphin_gfx_settings.set("Settings", "ShaderCompilationMode", "0")

        # Shader pre-caching
        if system.isOptSet("wait_for_shaders") and system.getOptBoolean(
            "wait_for_shaders",
        ):
            if (
                system.isOptSet("gfxbackend")
                and system.config["gfxbackend"] == "Vulkan"
            ):
                dolphin_gfx_settings.set(
                    "Settings", "WaitForShadersBeforeStarting", "True",
                )
            else:
                dolphin_gfx_settings.set(
                    "Settings", "WaitForShadersBeforeStarting", "False",
                )
        else:
            dolphin_gfx_settings.set(
                "Settings", "WaitForShadersBeforeStarting", "False",
            )

        # Various performance hacks - Default Off
        if system.isOptSet("perf_hacks") and system.getOptBoolean("perf_hacks"):
            dolphin_gfx_settings.set("Hacks", "BBoxEnable", "False")
            dolphin_gfx_settings.set("Hacks", "DeferEFBCopies", "True")
            dolphin_gfx_settings.set("Hacks", "EFBEmulateFormatChanges", "False")
            dolphin_gfx_settings.set("Hacks", "EFBScaledCopy", "True")
            dolphin_gfx_settings.set("Hacks", "EFBToTextureEnable", "True")
            dolphin_gfx_settings.set("Hacks", "SkipDuplicateXFBs", "True")
            dolphin_gfx_settings.set("Hacks", "XFBToTextureEnable", "True")
            dolphin_gfx_settings.set("Enhancements", "ForceFiltering", "True")
            dolphin_gfx_settings.set("Enhancements", "ArbitraryMipmapDetection", "True")
            dolphin_gfx_settings.set("Enhancements", "DisableCopyFilter", "True")
            dolphin_gfx_settings.set("Enhancements", "ForceTrueColor", "True")
        else:
            if dolphin_gfx_settings.has_section("Hacks"):
                dolphin_gfx_settings.remove_option("Hacks", "BBoxEnable")
                dolphin_gfx_settings.remove_option("Hacks", "DeferEFBCopies")
                dolphin_gfx_settings.remove_option("Hacks", "EFBEmulateFormatChanges")
                dolphin_gfx_settings.remove_option("Hacks", "EFBScaledCopy")
                dolphin_gfx_settings.remove_option("Hacks", "EFBToTextureEnable")
                dolphin_gfx_settings.remove_option("Hacks", "SkipDuplicateXFBs")
                dolphin_gfx_settings.remove_option("Hacks", "XFBToTextureEnable")
            if dolphin_gfx_settings.has_section("Enhancements"):
                dolphin_gfx_settings.remove_option("Enhancements", "ForceFiltering")
                dolphin_gfx_settings.remove_option(
                    "Enhancements", "ArbitraryMipmapDetection",
                )
                dolphin_gfx_settings.remove_option("Enhancements", "DisableCopyFilter")
                dolphin_gfx_settings.remove_option("Enhancements", "ForceTrueColor")

        if system.isOptSet("vbi_hack") and system.getOptBoolean("vbi_hack"):
            dolphin_gfx_settings.set("Hacks", "VISkip", "True")
        else:
            dolphin_gfx_settings.set("Hacks", "VISkip", "False")

        # Internal resolution settings
        if system.isOptSet("internal_resolution"):
            dolphin_gfx_settings.set(
                "Settings", "InternalResolution", system.config["internal_resolution"],
            )
        else:
            dolphin_gfx_settings.set("Settings", "InternalResolution", "1")

        # VSync
        if system.isOptSet("vsync") and not system.getOptBoolean("vsync"):
            dolphin_gfx_settings.set("Hardware", "VSync", "False")
        else:
            dolphin_gfx_settings.set("Hardware", "VSync", "True")

        # Anisotropic filtering
        if system.isOptSet("anisotropic_filtering"):
            dolphin_gfx_settings.set(
                "Enhancements", "MaxAnisotropy", system.config["anisotropic_filtering"],
            )
        else:
            dolphin_gfx_settings.set("Enhancements", "MaxAnisotropy", "0")

        # Anti aliasing
        if system.isOptSet("antialiasing"):
            dolphin_gfx_settings.set("Settings", "MSAA", system.config["antialiasing"])
        else:
            dolphin_gfx_settings.set("Settings", "MSAA", "0")

        # Anti aliasing mode
        if system.isOptSet("use_ssaa") and system.getOptBoolean("use_ssaa"):
            dolphin_gfx_settings.set("Settings", "SSAA", "True")
        else:
            dolphin_gfx_settings.set("Settings", "SSAA", "False")

        # Manual texture sampling
        # Setting on = speed hack off. Setting off = speed hack on
        if system.isOptSet("manual_texture_sampling") and system.getOptBoolean(
            "manual_texture_sampling",
        ):
            dolphin_gfx_settings.set("Hacks", "FastTextureSampling", "False")
        else:
            dolphin_gfx_settings.set("Hacks", "FastTextureSampling", "True")

        # Save gfx.ini
        with open(DOLPHIN_GFX_PATH, "w") as configfile:
            dolphin_gfx_settings.write(configfile)

        # Hotkeys.ini - overwrite to avoid issues
        hotkey_config = ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        hotkey_config.optionxform = lambda optionstr: str(optionstr)
        # [Hotkeys]
        hotkey_config.add_section("Hotkeys")
        # General - use virtual for now
        hotkey_config.set("Hotkeys", "Device", "XInput2/0/Virtual core pointer")
        hotkey_config.set("Hotkeys", "General/Open", "@(Ctrl+O)")
        hotkey_config.set("Hotkeys", "General/Toggle Pause", "F10")
        hotkey_config.set("Hotkeys", "General/Stop", "Escape")
        hotkey_config.set("Hotkeys", "General/Toggle Fullscreen", "@(Alt+Return)")
        hotkey_config.set("Hotkeys", "General/Take Screenshot", "F9")
        hotkey_config.set("Hotkeys", "General/Exit", "@(Shift+F11)")
        # Emulation Speed
        hotkey_config.set(
            "Hotkeys", "Emulation Speed/Disable Emulation Speed Limit", "Tab",
        )
        # Stepping
        hotkey_config.set("Hotkeys", "Stepping/Step Into", "F11")
        hotkey_config.set("Hotkeys", "Stepping/Step Over", "@(Shift+F10)")
        hotkey_config.set("Hotkeys", "Stepping/Step Out", "@(Shift+F11)")
        # Breakpoint
        hotkey_config.set("Hotkeys", "Breakpoint/Toggle Breakpoint", "@(Shift+F9)")
        # Wii
        hotkey_config.set("Hotkeys", "Wii/Connect Wii Remote 1", "@(Alt+F5)")
        hotkey_config.set("Hotkeys", "Wii/Connect Wii Remote 2", "@(Alt+F6)")
        hotkey_config.set("Hotkeys", "Wii/Connect Wii Remote 3", "@(Alt+F7)")
        hotkey_config.set("Hotkeys", "Wii/Connect Wii Remote 4", "@(Alt+F8)")
        hotkey_config.set("Hotkeys", "Wii/Connect Balance Board", "@(Alt+F9)")
        # Select
        hotkey_config.set(
            "Hotkeys", "Other State Hotkeys/Increase Selected State Slot", "@(Shift+F1)",
        )
        hotkey_config.set(
            "Hotkeys", "Other State Hotkeys/Decrease Selected State Slot", "@(Shift+F2)",
        )
        # Load
        hotkey_config.set("Hotkeys", "Load State/Load from Selected Slot", "F8")
        # Save State
        hotkey_config.set("Hotkeys", "Save State/Save to Selected Slot", "F5")
        # Other State Hotkeys
        hotkey_config.set(
            "Hotkeys", "Other State Hotkeys/Undo Load State", "@(Shift+F12)",
        )
        # GBA Core
        hotkey_config.set("Hotkeys", "GBA Core/Load ROM", "@(`Ctrl`+`Shift`+`O`)")
        hotkey_config.set("Hotkeys", "GBA Core/Unload ROM", "@(`Ctrl`+`Shift`+`W`)")
        hotkey_config.set("Hotkeys", "GBA Core/Reset", "@(`Ctrl`+`Shift`+`R`)")
        # GBA Volume
        hotkey_config.set("Hotkeys", "GBA Volume/Volume Down", "`KP_Subtract`")
        hotkey_config.set("Hotkeys", "GBA Volume/Volume Up", "`KP_Add`")
        hotkey_config.set("Hotkeys", "GBA Volume/Volume Toggle Mute", "`M`")
        # GBA Window Size
        hotkey_config.set("Hotkeys", "GBA Window Size/1x", "`KP_1`")
        hotkey_config.set("Hotkeys", "GBA Window Size/2x", "`KP_2`")
        hotkey_config.set("Hotkeys", "GBA Window Size/3x", "`KP_3`")
        hotkey_config.set("Hotkeys", "GBA Window Size/4x", "`KP_4`")
        # Skylanders Portal
        hotkey_config.set(
            "Hotkeys", "USB Emulation Devices/Show Skylanders Portal", "@(Ctrl+P)",
        )
        hotkey_config.set(
            "Hotkeys", "USB Emulation Devices/Show Infinity Base", "@(Ctrl+I)",
        )
        #
        # Write the configuration to the file
        hotkey_path = Path("/userdata/system/configs/dolphin-emu/Hotkeys.ini")
        with open(hotkey_path, "w") as configfile:
            hotkey_config.write(configfile)

        # Retroachievements
        rac_config = ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        rac_config.optionxform = lambda optionstr: str(optionstr)
        # [Achievements]
        rac_config.add_section("Achievements")
        if system.isOptSet("retroachievements") and system.getOptBoolean(
            "retroachievements",
        ):
            rac_config.set("Achievements", "Enabled", "True")
            rac_config.set("Achievements", "AchievementsEnabled", "True")
            username = system.config.get("retroachievements.username", "")
            token = system.config.get("retroachievements.token", "")
            hardcore = system.config.get("retroachievements.hardcore", "False")
            presence = system.config.get("retroachievements.richpresence", "False")
            leaderbd = system.config.get("retroachievements.leaderboard", "False")
            progress = system.config.get(
                "retroachievements.challenge_indicators", "False",
            )
            encore = system.config.get("retroachievements.encore", "False")
            verbose = system.config.get("retroachievements.verbose", "False")
            rac_config.set("Achievements", "Username", username)
            rac_config.set("Achievements", "ApiToken", token)
            rac_config.set("Achievements", "HardcoreEnabled", hardcore)
            rac_config.set("Achievements", "BadgesEnabled", verbose)
            rac_config.set("Achievements", "EncoreEnabled", encore)
            rac_config.set("Achievements", "ProgressEnabled", progress)
            rac_config.set("Achievements", "LeaderboardsEnabled", leaderbd)
            rac_config.set("Achievements", "RichPresenceEnabled", presence)
        else:
            rac_config.set("Achievements", "Enabled", "False")
            rac_config.set("Achievements", "AchievementsEnabled", "False")
        # Write the configuration to the file
        rac_path = Path("/userdata/system/configs/dolphin-emu/RetroAchievements.ini")
        with open(rac_path, "w") as rac_configfile:
            rac_config.write(rac_configfile)

        # Update SYSCONF
        with suppress(Exception):
            updateConfig(system.config, DOLPHIN_SYSCONF_PATH, game_resolution)

        # Check what version we've got
        if Path(DOLPHIN_BIN_PATH).is_file():
            # use the -b 'batch' option for nicer exit
            command_array = [DOLPHIN_BIN_PATH, "-b", "-e", rom]
        else:
            command_array = ["dolphin-emu-nogui", "-e", rom]

        # state_slot option
        if system.isOptSet("state_filename"):
            command_array.extend(["--save_state", system.config["state_filename"]])

        return Command(array=command_array)

    def get_in_game_ratio(
        self, config: Any, game_resolution: dict[str, int], rom: str,
    ) -> float:
        dolphinGFXSettings = ConfigParser(interpolation=None)
        # To prevent ConfigParser from converting to lower case
        dolphinGFXSettings.optionxform = lambda optionstr: str(optionstr)
        dolphinGFXSettings.read(DOLPHIN_GFX_PATH)

        dolphin_aspect_ratio = dolphinGFXSettings.get("Settings", "AspectRatio")
        # What if we're playing a GameCube game with the widescreen patch or not?
        if "widescreen_hack" in config and config["widescreen_hack"] == "1":
            wii_tv_mode = 1
        else:
            wii_tv_mode = 0

        with suppress(ValueError, TypeError, AttributeError):
            wii_tv_mode = getRatioFromConfig(config, game_resolution)

        # Auto
        if dolphin_aspect_ratio == "0":
            if wii_tv_mode == 1:
                return 16 / 9
            return 4 / 3

        # Forced 16:9
        if dolphin_aspect_ratio == "1":
            return 16 / 9

        # Forced 4:3
        if dolphin_aspect_ratio == "2":
            return 4 / 3

        # Stretched (thus depends on physical screen geometry)
        if dolphin_aspect_ratio == "3":
            return game_resolution["width"] / game_resolution["height"]

        return 4 / 3


# Get the language from the environment if user didn't set it in ES.
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
