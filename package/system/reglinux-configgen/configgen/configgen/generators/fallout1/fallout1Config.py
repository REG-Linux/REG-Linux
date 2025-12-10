from configgen.systemFiles import CONF, ROMS

FALLOUT_CONFIG_DIR = CONF + "/fallout1"
FALLOUT_CONFIG_PATH = FALLOUT_CONFIG_DIR + "/fallout.cfg"
FALLOUT_CONFIG_INI = FALLOUT_CONFIG_DIR + "/f1_res.ini"
FALLOUT_ROMS_DIR = ROMS + "/fallout1-ce"
FALLOUT_BIN_PATH = "/usr/bin/fallout1-ce"
FALLOUT_EXE_SOURCE_PATH = FALLOUT_ROMS_DIR + "/fallout1-ce"
FALLOUT_CONFIG_SOURCE_PATH = FALLOUT_ROMS_DIR + "/fallout1.cfg"
FALLOUT_CONFIG_INI_SOURCE_PATH = FALLOUT_ROMS_DIR + "/f1_res.ini"


def setFalloutConfig(falloutConfig, system):
    if not falloutConfig.has_section("debug"):
        falloutConfig.add_section("debug")
    if not falloutConfig.has_section("preferences"):
        falloutConfig.add_section("preferences")
        if not falloutConfig.has_section("sound"):
            falloutConfig.add_section("sound")
            if not falloutConfig.has_section("system"):
                falloutConfig.add_section("system")

    # fix linux path issues
    falloutConfig.set("sound", "music_path1", "DATA/SOUND/MUSIC/")
    falloutConfig.set("sound", "music_path2", "DATA/SOUND/MUSIC/")

    falloutConfig.set("system", "critter_dat", "CRITTER.DAT")
    falloutConfig.set("system", "critter_patches", "DATA")
    falloutConfig.set("system", "master_dat", "MASTER.DAT")
    falloutConfig.set("system", "master_patches", "DATA")

    if system.isOptSet("fout1_game_difficulty"):
        falloutConfig.set(
            "preferences", "game_difficulty", system.config["fout1_game_difficulty"]
        )
    else:
        falloutConfig.set("preferences", "game_difficulty", "1")

    if system.isOptSet("fout1_combat_difficulty"):
        falloutConfig.set(
            "preferences", "combat_difficulty", system.config["fout1_combat_difficulty"]
        )
    else:
        falloutConfig.set("preferences", "combat_difficulty", "1")

    if system.isOptSet("fout1_violence_level"):
        falloutConfig.set(
            "preferences", "violence_level", system.config["fout1_violence_level"]
        )
    else:
        falloutConfig.set("preferences", "violence_level", "2")

    if system.isOptSet("fout1_subtitles"):
        falloutConfig.set("preferences", "subtitles", system.config["fout1_subtitles"])
    else:
        falloutConfig.set("preferences", "subtitles", "0")

    if system.isOptSet("fout1_language"):
        falloutConfig.set("system", "language", system.config["fout1_language"])
    else:
        falloutConfig.set("system", "language", "english")


def setFalloutIniConfig(falloutIniConfig, gameResolution):
    # [MAIN]
    if not falloutIniConfig.has_section("MAIN"):
        falloutIniConfig.add_section("MAIN")

    # Note: This will increase the minimum resolution to from 640x480 to 1280x960.
    if gameResolution["width"] >= 1280 and gameResolution["height"] >= 960:
        falloutIniConfig.set("MAIN", "SCALE_2X", "1")
    else:
        falloutIniConfig.set("MAIN", "SCALE_2X", "0")
    falloutIniConfig.set("MAIN", "SCR_WIDTH", format(gameResolution["width"]))
    falloutIniConfig.set("MAIN", "SCR_HEIGHT", format(gameResolution["height"]))

    # fullscreen
    falloutIniConfig.set("MAIN", "WINDOWED", "0")
