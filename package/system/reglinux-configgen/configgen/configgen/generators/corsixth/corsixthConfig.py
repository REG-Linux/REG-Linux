from os import chdir
from subprocess import CalledProcessError, check_output
from typing import Any

from configgen.systemFiles import CONF, ROMS, SAVES, SCREENSHOTS
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

CORSIXTH_CONFIG_DIR = CONF + "/CorsixTH"
CORSIXTH_CONFIG_PATH = CORSIXTH_CONFIG_DIR + "/config.txt"
CORSIXTH_SAVES_DIR = SAVES + "/corsixth"
CORSIXTH_ROMS_DIR = ROMS + "/corsixth"
CORSIXTH_FONT_PATH = "/usr/share/fonts/dejavu/DejaVuSans.ttf"
CORSIXTH_SCREENSCHOTS_DIR = SCREENSHOTS + "/corsixth"
CORSIXTH_BIN_PATH = "/usr/bin/corsix-th"
CORSIXTH_GAME_DATA_DIR = [
    "/userdata/roms/corsixth/ANIMS",
    "/userdata/roms/corsixth/DATA",
    "/userdata/roms/corsixth/INTRO",
    "/userdata/roms/corsixth/LEVELS",
    "/userdata/roms/corsixth/QDATA",
]


def setCorsixthConfig(corsixthConfig: Any, system: Any, gameResolution: Any) -> None:
    corsixthConfig.write("check_for_updates = false\n")
    corsixthConfig.write("theme_hospital_install = [[" + CORSIXTH_ROMS_DIR + "]]\n")
    corsixthConfig.write("unicode_font = [[" + CORSIXTH_FONT_PATH + "]]\n")
    corsixthConfig.write("savegames = [[" + CORSIXTH_SAVES_DIR + "]]\n")
    corsixthConfig.write("screenshots = [[" + CORSIXTH_SCREENSCHOTS_DIR + "]]\n")

    # Values coming from ES configuration : Resolution
    corsixthConfig.write("fullscreen = true\n")
    if gameResolution["width"] < gameResolution["height"]:
        gameResolution["width"], gameResolution["height"] = (
            gameResolution["height"],
            gameResolution["width"],
        )
    corsixthConfig.write("width = " + str(gameResolution["width"]) + "\n")
    corsixthConfig.write("height = " + str(gameResolution["height"]) + "\n")

    # Values coming from ES configuration : New Graphics
    if system.isOptSet("cth_new_graphics"):
        corsixthConfig.write(
            "use_new_graphics = " + system.config["cth_new_graphics"] + "\n"
        )
    else:
        corsixthConfig.write("use_new_graphics = true\n")

    # Values coming from ES configuration : Sandbox Mode
    if system.isOptSet("cth_free_build_mode"):
        corsixthConfig.write(
            "free_build_mode = " + system.config["cth_free_build_mode"] + "\n"
        )
    else:
        corsixthConfig.write("free_build_mode = false\n")

    # Values coming from ES configuration : Intro Movie
    if system.isOptSet("cth_play_intro"):
        corsixthConfig.write("play_intro = " + system.config["cth_play_intro"] + "\n")
    else:
        corsixthConfig.write("play_intro = true\n")

    # Now auto-set the language from reglinux ES locale
    language_mapping = {
        "en_US": "en",
        "en_GB": "en",
        "fr_FR": "fr",
        "oc_FR": "fr",
        "de_DE": "de",
        "es_ES": "es",
        "es_MX": "es",
        "it_IT": "it",
        "nl_NL": "nl",
        "ru_RU": "ru",
        "sv_SE": "sv",
        "cs_CZ": "cs",
        "fi_FI": "fi",
        "pl_PL": "pl",
        "hu_HU": "hu",
        "pt_PT": "pt",
        "pt_BR": "br",
        "zh_CN": "zhs",
        "zh_TW": "zht",
        "ko_KR": "ko",
        "nb_NO": "nb",
        "nn_NO": "nb",
    }
    # 1. Grab reglinux system language
    try:
        language = check_output(
            "/usr/bin/system-settings-get system.language", shell=True, text=True
        ).strip()
    except CalledProcessError:
        language = "en_US"
    # 2. Map it
    corsixthLanguage = language_mapping.get(language, "en")
    # 3. Write it
    corsixthConfig.write("language = [[" + corsixthLanguage + "]]\n")

    # Check custom music is installed
    try:
        chdir(CORSIXTH_ROMS_DIR + "/MP3")
        corsixthConfig.write("audio_music = [[" + CORSIXTH_ROMS_DIR + "/MP3" + "]]\n")
    except (FileNotFoundError, OSError) as e:
        eslog.debug(
            f"Corsixth: Music directory not found: {CORSIXTH_ROMS_DIR}/MP3 - {str(e)}"
        )
        corsixthConfig.write("audio_music = nil\n")
