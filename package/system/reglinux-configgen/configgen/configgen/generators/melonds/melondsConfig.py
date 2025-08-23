from systemFiles import CONF, SAVES, CHEATS

MELONDS_CONFIG_DIR = CONF + '/melonDS'
MELONDS_CONFIG_PATH = MELONDS_CONFIG_DIR + '/melonDS.ini'
MELONDS_SAVES_DIR = SAVES + '/melonDS'
MELONDS_CHEATS_DIR = CHEATS + '/melonDS'
MELONDS_BIN_PATH = '/usr/bin/melonDS'

def setMelonDSConfig(melondsConfig, system, gameResolution):
    if gameResolution["width"] < gameResolution["height"]:
        width, height = gameResolution["height"], gameResolution["width"]
    else:
        width, height = gameResolution["width"], gameResolution["height"]

    # [Set config defaults]
    config_lines = [
        "WindowWidth={}\n".format(width),
        "WindowHeight={}\n".format(height),
        "WindowMax=1\n",
        # Hide mouse after 5 seconds
        "MouseHide=1\n",
        "MouseHideSeconds=5\n",
        # Set bios locations
        "ExternalBIOSEnable=1\n",
        "BIOS9Path=/userdata/bios/bios9.bin\n",
        "BIOS7Path=/userdata/bios/bios7.bin\n",
        "FirmwarePath=/userdata/bios/firmware.bin\n",
        "DSiBIOS9Path=/userdata/bios/dsi_bios9.bin\n",
        "DSiBIOS7Path=/userdata/bios/dsi_bios7.bin\n",
        "DSiFirmwarePath=/userdata/bios/dsi_firmware.bin\n",
        "DSiNANDPath=/userdata/bios/dsi_nand.bin\n",
        # Set save locations
        "DLDIFolderPath=/userdata/saves/melonds\n",
        "DSiSDFolderPath=/userdata/saves/melonds\n",
        "MicWavPath=/userdata/saves/melonds\n",
        "SaveFilePath=/userdata/saves/melonds\n",
        "SavestatePath=/userdata/saves/melonds\n",
        # Cheater!
        "CheatFilePath=/userdata/cheats/melonDS\n",
        # Roms
        "LastROMFolder=/userdata/roms/nds\n",
        # Audio
        "AudioInterp=1\n",
        "AudioBitrate=2\n",
        "AudioVolume=256\n",
        # For Software Rendering
        "Threaded3D=1\n",
    ]

    # Write all default config lines
    for line in config_lines:
        melondsConfig.write(line)

    # [User selected options]
    # MelonDS only has OpenGL or Software - use OpenGL if not selected
    if system.isOptSet("melonds_renderer"):
        melondsConfig.write("3DRenderer={}\n".format(system.config["melonds_renderer"]))
    else:
        melondsConfig.write("3DRenderer=1\n")
    if system.isOptSet("melonds_framerate"):
        melondsConfig.write("LimitFPS={}\n".format(system.config["melonds_framerate"]))
    else:
        melondsConfig.write("LimitFPS=1\n")
    if system.isOptSet("melonds_resolution"):
        melondsConfig.write("GL_ScaleFactor={}\n".format(system.config["melonds_resolution"]))
    else:
        melondsConfig.write("GL_ScaleFactor=1\n")
    if system.isOptSet("melonds_polygons"):
        melondsConfig.write("GL_BetterPolygons={}\n".format(system.config["melonds_polygons"]))
    else:
        melondsConfig.write("GL_BetterPolygons=0\n")
    if system.isOptSet("melonds_rotation"):
        melondsConfig.write("ScreenRotation={}\n".format(system.config["melonds_rotation"]))
    else:
        melondsConfig.write("ScreenRotation=0\n")
    if system.isOptSet("melonds_screenswap"):
        melondsConfig.write("ScreenSwap={}\n".format(system.config["melonds_screenswap"]))
    else:
        melondsConfig.write("ScreenSwap=0\n")
    if system.isOptSet("melonds_layout"):
        melondsConfig.write("ScreenLayout={}\n".format(system.config["melonds_layout"]))
    else:
        melondsConfig.write("ScreenLayout=0\n")
    if system.isOptSet("melonds_screensizing"):
        melondsConfig.write("ScreenSizing={}\n".format(system.config["melonds_screensizing"]))
    else:
        melondsConfig.write("ScreenSizing=0\n")
    if system.isOptSet("melonds_scaling"):
        melondsConfig.write("IntegerScaling={}\n".format(system.config["melonds_scaling"]))
    else:
        melondsConfig.write("IntegerScaling=0\n")
    # Cheater!
    if system.isOptSet("melonds_cheats"):
        melondsConfig.write("EnableCheats={}\n".format(system.config["melonds_cheats"]))
    else:
        melondsConfig.write("EnableCheats=0\n")
    if system.isOptSet("melonds_osd"):
        melondsConfig.write("ShowOSD={}\n".format(system.config["melonds_osd"]))
    else:
        melondsConfig.write("ShowOSD=1\n")
    if system.isOptSet("melonds_console"):
        melondsConfig.write("ConsoleType={}\n".format(system.config["melonds_console"]))
    else:
        melondsConfig.write("ConsoleType=0\n")
