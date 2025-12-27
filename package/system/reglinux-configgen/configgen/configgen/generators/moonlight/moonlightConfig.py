from typing import Any

from configgen.systemFiles import CONF

MOONLIGHT_CONFIG_DIR = CONF + "/moonlight"
MOONLIGHT_CONFIG_PATH = MOONLIGHT_CONFIG_DIR + "/moonlight.conf"
MOONLIGHT_STAGING_CONFIG_PATH = MOONLIGHT_CONFIG_DIR + "/staging/moonlight.conf"
MOONLIGHT_GAMELIST_PATH = MOONLIGHT_CONFIG_DIR + "/gamelist.txt"
MOONLIGHT_MAPPING_PATH = {
    1: MOONLIGHT_CONFIG_DIR + "/mappingP1.conf",
    2: MOONLIGHT_CONFIG_DIR + "/mappingP2.conf",
    3: MOONLIGHT_CONFIG_DIR + "/mappingP3.conf",
    4: MOONLIGHT_CONFIG_DIR + "/mappingP4.conf",
}
MOONLIGHT_BIN_PATH = "/usr/bin/moonlight"


def setMoonlightConfig(moonlightConfig: Any, system: Any) -> None:
    # resolution
    resolutions = {
        "0": ("1280", "720"),
        "1": ("1920", "1080"),
        "2": ("3840", "2160"),
    }
    if system.isOptSet("moonlight_resolution"):
        width, height = resolutions.get(
            system.config["moonlight_resolution"], ("1280", "720")
        )
    else:
        width, height = "1280", "720"
    moonlightConfig.save("width", width)
    moonlightConfig.save("height", height)

    # rotate
    if system.isOptSet("moonlight_rotate"):
        moonlightConfig.save("rotate", system.config["moonlight_rotate"])
    else:
        moonlightConfig.save("rotate", "0")

    # framerate
    framerates = {"0": "30", "1": "60", "2": "120"}
    if system.isOptSet("moonlight_framerate"):
        fps = framerates.get(system.config["moonlight_framerate"], "60")
    else:
        fps = "60"
    moonlightConfig.save("fps", fps)

    # bitrate
    bitrates = {
        "0": "5000",
        "1": "10000",
        "2": "20000",
        "3": "50000",
    }
    if system.isOptSet("moonlight_bitrate"):
        bitrate = bitrates.get(system.config["moonlight_bitrate"], "-1")
    else:
        bitrate = "-1"  # -1 sets Moonlight default
    moonlightConfig.save("bitrate", bitrate)

    # codec
    if system.isOptSet("moonlight_codec"):
        moonlightConfig.save("codec", system.config["moonlight_codec"])
    else:
        moonlightConfig.save("codec", "auto")

    # sops (Streaming Optimal Playable Settings)
    if system.isOptSet("moonlight_sops"):
        moonlightConfig.save("sops", system.config["moonlight_sops"].lower())
    else:
        moonlightConfig.save("sops", "true")

    # quit remote app on exit
    if system.isOptSet("moonlight_quitapp"):
        moonlightConfig.save("quitappafter", system.config["moonlight_quitapp"].lower())
    else:
        moonlightConfig.save("quitappafter", "false")

    # view only
    if system.isOptSet("moonlight_viewonly"):
        moonlightConfig.save("viewonly", system.config["moonlight_viewonly"].lower())
    else:
        moonlightConfig.save("viewonly", "false")

    # platform - we only select sdl (best compatibility)
    # required for controllers to work
    moonlightConfig.save("platform", "sdl")

    # Directory to store encryption keys
    moonlightConfig.save("keydir", MOONLIGHT_CONFIG_DIR + "/keydir")

    # lan or wan streaming - ideally lan
    if system.isOptSet("moonlight_remote"):
        moonlightConfig.save("remote", system.config["moonlight_remote"])
    else:
        moonlightConfig.save("remote", "no")

    # Enable 5.1/7.1 surround sound
    if system.isOptSet("moonlight_surround"):
        moonlightConfig.save("surround", system.config["moonlight_surround"])
    else:
        moonlightConfig.save("#surround", "5.1")
