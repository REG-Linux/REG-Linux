#!/usr/bin/env python

from utils.logger import get_logger

eslog = get_logger(__name__)

def setMednafenConfig(cfgConfig):

    # Enable (automatic) usage of this module.
    cfgConfig.write("apple2.enable 1\n")
    cfgConfig.write("gb.enable 1\n")
    cfgConfig.write("gba.enable 1\n")
    cfgConfig.write("gg.enable 1\n")
    cfgConfig.write("lynx.enable 1\n")
    cfgConfig.write("md.enable 1\n")
    cfgConfig.write("nes.enable 1\n")
    cfgConfig.write("ngp.enable 1\n")
    cfgConfig.write("pce.enable 1\n")
    cfgConfig.write("pce_fast.enable 1\n")
    cfgConfig.write("pcfx.enable 1\n")
    cfgConfig.write("psx.enable 1\n")
    cfgConfig.write("sasplay.enable 1\n")
    cfgConfig.write("sms.enable 1\n")
    cfgConfig.write("snes.enable 1\n")
    cfgConfig.write("snes_faust.enable 1\n")
    cfgConfig.write("ss.enable 1\n")
    cfgConfig.write("ssfplay.enable 1\n")
    cfgConfig.write("vb.enable 1\n")
    cfgConfig.write("wswan.enable 1\n")

    # Stretch to fill screen.
    cfgConfig.write("apple2.stretch full\n")
    cfgConfig.write("gb.stretch full\n")
    cfgConfig.write("gba.stretch full\n")
    cfgConfig.write("gg.stretch full\n")
    cfgConfig.write("lynx.stretch full\n")
    cfgConfig.write("md.stretch full\n")
    cfgConfig.write("nes.stretch full\n")
    cfgConfig.write("ngp.stretch full\n")
    cfgConfig.write("pce.stretch full\n")
    cfgConfig.write("pce_fast.stretch full\n")
    cfgConfig.write("pcfx.stretch full\n")
    cfgConfig.write("psx.stretch full\n")
    cfgConfig.write("sasplay.stretch full\n")
    cfgConfig.write("sms.stretch full\n")
    cfgConfig.write("snes.stretch full\n")
    cfgConfig.write("snes_faust.stretch full\n")
    cfgConfig.write("ss.stretch full\n")
    cfgConfig.write("ssfplay.stretch full\n")
    cfgConfig.write("vb.stretch full\n")
    cfgConfig.write("wswan.stretch full\n")

    # Select sound driver.
    cfgConfig.write("sound.driver sdl\n")

    # Enable sound output.
    cfgConfig.write("sound 1\n")

    # Enable fullscreen mode.
    cfgConfig.write("video.fs 1\n")
    cfgConfig.write("video.fs.display -1\n")

    # Path to directory for firmware.
    cfgConfig.write("filesys.path_firmware firmware\n")

    # Automatically load/save state on game load/close.
    cfgConfig.write("autosave 0\n")

    # Enable cheats.
    cfgConfig.write("cheats 0\n")

    # Exit
    cfgConfig.write("command.exit keyboard 0x0 69\n")

    # Fast-forward
    cfgConfig.write("command.fast_forward keyboard 0x0 53\n")

    # Rewind
    cfgConfig.write("command.state_rewind keyboard 0x0 42\n")

    # Reset
    cfgConfig.write("command.reset keyboard 0x0 67\n")

    # Rotate screen
    cfgConfig.write("command.rotate_screen keyboard 0x0 18+alt\n")

    # Automatically enable FPS display on startup.
    cfgConfig.write("fps.autoenable 0\n")

