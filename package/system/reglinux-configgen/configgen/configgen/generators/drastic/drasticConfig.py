from os import environ
from configgen.systemFiles import CONF

DRASTIC_CONFIG_DIR = "/usr/share/drastic"
DRASTIC_CONFIG_DIR_USER = CONF + "/drastic"
DRASTIC_CONFIG_PATH = DRASTIC_CONFIG_DIR_USER + "/config/drastic.cfg"
DRASTIC_BIN_PATH = "/usr/bin/drastic"


def setDrasticConfig(drasticConfig, system):
    # Getting Values from ES
    if system.isOptSet("drastic_hires") and system.config["drastic_hires"] == "1":
        esvaluedrastichires = 1
    else:
        esvaluedrastichires = 0

    if system.isOptSet("drastic_threaded") and system.config["drastic_threaded"] == "1":
        esvaluedrasticthreaded = 1
    else:
        esvaluedrasticthreaded = 0

    if system.isOptSet("drastic_fix2d") and system.config["drastic_fix2d"] == "1":
        esvaluedrasticfix2d = 1
    else:
        esvaluedrasticfix2d = 0

    if system.isOptSet("drastic_screen_orientation"):
        esvaluedrasticscreenorientation = system.config["drastic_screen_orientation"]
    else:
        esvaluedrasticscreenorientation = 0

    # Default to none as auto seems to be bugged (just reduces framerate by half, even when the system is otherwise capable of running at 60fps, even the rpi3 can do this).
    if system.isOptSet("drastic_frameskip_type"):
        esvaluedrasticframeskiptype = system.config["drastic_frameskip_type"]
    else:
        esvaluedrasticframeskiptype = 0

    if system.isOptSet("drastic_frameskip_value"):
        esvaluedrasticframeskipvalue = system.config["drastic_frameskip_value"]
    else:
        esvaluedrasticframeskipvalue = 1

    textList = [  # 0,1,2,3 ...
        "enable_sound" + " = 1",
        "compress_savestates" + " = 1",
        "savestate_snapshot" + " = 1",
        "firmware.username" + " = REGLinux",
        "firmware.language" + " = " + str(getDrasticLangFromEnvironment()),
        "firmware.favorite_color" + " = 11",
        "firmware.birthday_month" + " = 11",
        "firmware.birthday_day" + " = 25",
        "enable_cheats" + " = 1",
        "rtc_system_time" + " = 1",
        "use_rtc_custom_time" + " = 0",
        "rtc_custom_time" + " = 0",
        "frameskip_type" + " = " + str(esvaluedrasticframeskiptype),  # None/Manual/Auto
        "frameskip_value" + " = " + str(esvaluedrasticframeskipvalue),  # 1-9
        "safe_frameskip"
        + " = 1",  # Needed for automatic frameskipping to actually work.
        "disable_edge_marking"
        + " = 1",  # will prevent edge marking. It draws outlines around some 3D models to give a cel-shaded effect. Since DraStic doesn't emulate anti-aliasing, it'll cause edges to look harsher than they may on a real DS.
        "fix_main_2d_screen"
        + " = "
        + str(
            esvaluedrasticfix2d
        ),  # Top Screen will always be the Action Screen (for 2d games like Sonic)
        "hires_3d" + " = " + str(esvaluedrastichires),  # High Resolution 3D Rendering
        "threaded_3d"
        + " = "
        + str(
            esvaluedrasticthreaded
        ),  # MultiThreaded 3D Rendering - Improves perf in 3D - can cause glitch.
        "screen_orientation"
        + " = "
        + str(esvaluedrasticscreenorientation),  # Vertical/Horizontal/OneScreen
        "screen_scaling" + " = 0",  # No Scaling/Stretch Aspect/1x2x/2x1x/TvSplit
        "screen_swap " + " = 0",
    ]

    # Write the cfg file
    for line in textList:
        drasticConfig.write(line)
        drasticConfig.write("\n")


# Language auto-setting
def getDrasticLangFromEnvironment():
    lang = environ["LANG"][:5]
    availableLanguages = {
        "ja_JP": 0,
        "en_US": 1,
        "fr_FR": 2,
        "de_DE": 3,
        "it_IT": 4,
        "es_ES": 5,
    }
    if lang in availableLanguages:
        return availableLanguages[lang]
    else:
        return availableLanguages["en_US"]
