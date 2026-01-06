from contextlib import suppress
from pathlib import Path
from typing import Any

from configgen.settings import TOMLSettings
from configgen.systemFiles import CONF, SAVES

XEMU_SAVES_DIR = SAVES / "xbox"
XEMU_CONFIG_PATH = CONF / "xemu" / "xemu.toml"
XEMU_BIN_PATH = Path("/usr/bin/xemu")


def setXemuConfig(
    system: Any,
    rom: str,
    playersControllers: Any,
    gameResolution: Any,
) -> None:
    # Create TOML settings instance
    settings = TOMLSettings(XEMU_CONFIG_PATH, auto_load=False)

    # Load existing config if it exists
    if XEMU_CONFIG_PATH.exists():
        with suppress(Exception):
            settings.load()

    createXemuConfig(settings, system, rom, playersControllers, gameResolution)

    # save the toml file
    config_dir = XEMU_CONFIG_PATH.parent
    if not config_dir.exists():
        config_dir.mkdir(parents=True, exist_ok=True)
    settings.write()


def createXemuConfig(
    settings: TOMLSettings,
    system: Any,
    rom: str,
    playersControllers: Any,
    gameResolution: Any,
) -> None:
    # Initialize sections if they don't exist
    if not settings.exists("general"):
        settings["general"] = {}
    if not settings.exists("sys"):
        settings["sys"] = {}
    if not settings.exists("sys.files"):
        settings["sys.files"] = {}
    if not settings.exists("audio"):
        settings["audio"] = {}
    if not settings.exists("display"):
        settings["display"] = {}
    if not settings.exists("display.quality"):
        settings["display.quality"] = {}
    if not settings.exists("display.window"):
        settings["display.window"] = {}
    if not settings.exists("display.ui"):
        settings["display.ui"] = {}
    if not settings.exists("input"):
        settings["input"] = {}
    if not settings.exists("input.bindings"):
        settings["input.bindings"] = {}
    if not settings.exists("net"):
        settings["net"] = {}
    if not settings.exists("net.udp"):
        settings["net.udp"] = {}

    # Get current config data to modify sections
    config_data = settings._data

    # Boot Animation Skip
    if system.isOptSet("xemu_bootanim"):
        config_data["general"]["skip_boot_anim"] = system.config["xemu_bootanim"]
    else:
        config_data["general"]["skip_boot_anim"] = False

    # Disable welcome screen on first launch
    config_data["general"]["show_welcome"] = False

    # Set Screenshot directory
    config_data["general"]["screenshot_dir"] = "/userdata/screenshots"

    # Fill sys sections
    if system.isOptSet("xemu_memory"):
        config_data["sys"]["mem_limit"] = system.config["xemu_memory"]
    else:
        config_data["sys"]["mem_limit"] = "64"

    if system.name == "chihiro":
        config_data["sys"]["mem_limit"] = "128"
        config_data["sys.files"]["flashrom_path"] = "/userdata/bios/cerbios.bin"
    else:
        config_data["sys.files"]["flashrom_path"] = "/userdata/bios/Complex_4627.bin"

    config_data["sys.files"]["bootrom_path"] = "/userdata/bios/mcpx_1.0.bin"
    config_data["sys.files"]["hdd_path"] = "/userdata/saves/xbox/xbox_hdd.qcow2"
    config_data["sys.files"]["eeprom_path"] = "/userdata/saves/xbox/xemu_eeprom.bin"
    config_data["sys.files"]["dvd_path"] = rom

    # Audio quality
    if system.isOptSet("xemu_use_dsp"):
        config_data["audio"]["use_dsp"] = system.config["xemu_use_dsp"]
    else:
        config_data["audio"]["use_dsp"] = False

    # Rendering resolution
    if system.isOptSet("xemu_render"):
        config_data["display.quality"]["surface_scale"] = system.config["xemu_render"]
    else:
        config_data["display.quality"]["surface_scale"] = 1  # render scale by default

    # start fullscreen
    config_data["display.window"]["fullscreen_on_startup"] = True

    # Window size
    window_res = f"{gameResolution['width']}x{gameResolution['height']}"
    config_data["display.window"]["startup_size"] = window_res

    # Vsync
    if system.isOptSet("xemu_vsync"):
        config_data["display.window"]["vsync"] = system.config["xemu_vsync"]
    else:
        config_data["display.window"]["vsync"] = True

    # don't show the menubar
    config_data["display.ui"]["show_menubar"] = False

    # Scaling
    if system.isOptSet("xemu_scaling"):
        config_data["display.ui"]["fit"] = system.config["xemu_scaling"]
    else:
        config_data["display.ui"]["fit"] = "scale"

    # Aspect ratio
    if system.isOptSet("xemu_aspect"):
        config_data["display.ui"]["aspect_ratio"] = system.config["xemu_aspect"]
    else:
        config_data["display.ui"]["aspect_ratio"] = "auto"

    # Fill input section
    # first, clear
    for i in range(1, 5):
        if (
            "input.bindings" in config_data
            and f"port{i}" in config_data["input.bindings"]
        ):
            del config_data["input.bindings"][f"port{i}"]
    nplayer = 1
    for _, pad in sorted(playersControllers.items()):
        if nplayer <= 4:
            config_data["input.bindings"][f"port{nplayer}"] = pad.guid
        nplayer = nplayer + 1

    # Network
    # Documentation: https://github.com/xemu-project/xemu/blob/master/config_spec.yml
    if system.isOptSet("xemu_networktype"):
        config_data["net"]["enable"] = True
        config_data["net"]["backend"] = system.config["xemu_networktype"]
    else:
        config_data["net"]["enable"] = False
    # Additional settings for udp: if nothing is entered in these fields, the xemu.toml is untouched
    if system.isOptSet("xemu_udpremote"):
        config_data["net.udp"]["remote_addr"] = system.config["xemu_udpremote"]
    if system.isOptSet("xemu_udpbind"):
        config_data["net.udp"]["bind_addr"] = system.config["xemu_udpbind"]
