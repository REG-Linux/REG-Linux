#!/usr/bin/env python
import os
import sys
import time
import subprocess
import csv
from .logger import get_logger

eslog = get_logger(__name__)

# Set a specific video mode
def changeMode(videomode):
    cmd = ["regmsg", "setMode", videomode]
    eslog.debug(f"setVideoMode({videomode}): {cmd}")
    max_tries = 2  # maximum number of tries to set the mode
    for i in range(max_tries):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            eslog.debug(result.stdout.strip())
            return
        except subprocess.CalledProcessError as e:
            eslog.error(f"Error setting video mode: {e.stderr}")
            if i == max_tries - 1:
                raise
            time.sleep(1)

def getCurrentMode():
    proc = subprocess.Popen(["regmsg currentMode"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    for val in out.decode().splitlines():
        return val # return the first line

def getScreensInfos(config):
    resolution1 = getCurrentResolution()
    outputs = getScreens()

    res = []
    res.append({"width": resolution1["width"], "height": resolution1["height"], "x": 0, "y": 0})

    if "videooutput2" not in config or len(outputs) <= 1:
        eslog.debug("Screens:")
        eslog.debug(res)
        return res

    resolution2 = getCurrentResolution(config["videooutput2"])
    res.append({"width": resolution2["width"], "height": resolution2["height"], "x": resolution1["width"], "y": 0})

    if "videooutput3" not in config or len(outputs) <= 2:
        eslog.debug("Screens:")
        eslog.debug(res)
        return res

    resolution3 = getCurrentResolution(config["videooutput3"])
    res.append({"width": resolution3["width"], "height": resolution3["height"], "x": resolution1["width"]+resolution2["width"], "y": 0})

    eslog.debug("Screens:")
    eslog.debug(res)
    return res

def getScreens():
    proc = subprocess.Popen(["regmsg listOutputs"], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    return out.decode().splitlines()

def minTomaxResolution():
    proc = subprocess.Popen(["regmsg minTomaxResolution"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

def getRefreshRate():
    proc = subprocess.Popen(["regmsg currentRefresh"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    for val in out.decode().splitlines():
        return val # return the first line

def getCurrentResolution(name = None):
    if name is None:
        proc = subprocess.Popen(["regmsg currentResolution"], stdout=subprocess.PIPE, shell=True)
    else:
        proc = subprocess.Popen(["regmsg --screen {} currentResolution".format(name)], stdout=subprocess.PIPE, shell=True)

    (out, err) = proc.communicate()
    vals = out.decode().split("x")
    return { "width": int(vals[0]), "height": int(vals[1]) }

def supportSystemRotation():
    proc = subprocess.Popen(["regmsg supportSystemRotation"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return proc.returncode == 0

def changeMouse(mode):
    eslog.debug(f"changeMouseMode({mode})")
    if mode:
        cmd = "system-mouse show"
    else:
        cmd = "system-mouse hide"
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

def getGLVersion():
    try:
        # optim for most sbc having not glxinfo
        if os.path.exists("/usr/bin/glxinfo") == False:
            return 0

        glxVerCmd = 'glxinfo | grep "OpenGL version"'
        glVerOutput = subprocess.check_output(glxVerCmd, shell=True).decode(sys.stdout.encoding)
        glVerString = glVerOutput.split()
        glVerTemp = glVerString[3].split(".")
        if len(glVerTemp) > 2:
            del glVerTemp[2:]
        glVersion = float('.'.join(glVerTemp))
        return glVersion
    except:
        return 0

def getGLVendor():
    try:
        # optim for most sbc having not glxinfo
        if os.path.exists("/usr/bin/glxinfo") == False:
            return "unknown"

        glxVendCmd = 'glxinfo | grep "OpenGL vendor string"'
        glVendOutput = subprocess.check_output(glxVendCmd, shell=True).decode(sys.stdout.encoding)
        glVendString = glVendOutput.split()
        glVendor = glVendString[3].casefold()
        return glVendor
    except:
        return "unknown"

def getAltDecoration(systemName, rom, emulator):
    # Returns an ID for games that need rotated bezels/shaders or have special art
    # Vectrex will actually return an abbreviated game name for overlays, all others will return 0, 90, or 270 for rotation angle
    # 0 will be ignored.
    # Currently in use with bezels & libretro shaders
    if not emulator in ['mame', 'retroarch']:
        return "standalone"

    if not systemName in ['lynx', 'wswan', 'wswanc', 'mame', 'fbneo', 'naomi', 'atomiswave', 'nds', '3ds', 'vectrex']:
        return "0"

    # Look for external file, exit if not set up
    specialFile = '/usr/share/reglinux/configgen/data/special/' + systemName + '.csv'
    if not os.path.exists(specialFile):
        return "0"

    romBasename = os.path.basename(rom)
    romName = os.path.splitext(romBasename)[0]
    romCompare = romName.casefold()

    # Load the file, read it in
    # Each file will be a csv with each row being the standard (ie No-Intro) filename, angle of rotation (90 or 270)
    # Case indifferent, rom file name and filenames in list will be folded
    openFile = open(specialFile, 'r')
    with openFile:
        specialList = csv.reader(openFile, delimiter=';')
        for row in specialList:
            if row[0].casefold() == romCompare:
                return str(row[1])

    return "0"
