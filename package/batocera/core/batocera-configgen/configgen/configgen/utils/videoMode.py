#!/usr/bin/env python
import csv
import os
import re
import subprocess
import sys

from utils.video.videoModeDrm import drmChangeMode, drmGetCurrentMode, drmGetCurrentResolution, drmMinTomaxResolution
from utils.video.videoModeWayland import waylandChangeMode, waylandGetCurrentMode, waylandGetCurrentResolution
from utils.video.videoModeX11 import X11ChangeMode, X11GetCurrentMode, X11GetCurrentResolution
from .logger import get_logger

eslog = get_logger(__name__)

# Set a specific video mode
def changeMode(videomode):
    return drmChangeMode(videomode)

def getCurrentMode():
    return drmGetCurrentMode()

def getCurrentResolution(name=None):
    return drmGetCurrentResolution(name)

def minTomaxResolution():
    current = getCurrentResolution()
    resolution = str(current["width"]) + "x" + str(current["height"])
    return drmMinTomaxResolution(resolution)

def getRefreshRate():
    proc = subprocess.Popen(["batocera-resolution refreshRate"], stdout=subprocess.PIPE, shell=True)
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
    res.append({"width": resolution3["width"], "height": resolution3["height"],
                "x": resolution1["width"] + resolution2["width"], "y": 0})

    eslog.debug("Screens:")
    eslog.debug(res)
    return res


def getScreens():
    proc = subprocess.Popen(["batocera-resolution listOutputs"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return out.decode().splitlines()


def supportSystemRotation():
    proc = subprocess.Popen(["batocera-resolution supportSystemRotation"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return proc.returncode == 0


def isResolutionReversed():
    return os.path.exists("/var/run/rk-rotation")


def checkModeExists(videomode):
    # max resolution given
    if videomode[0:4] == "max-":
        matches = re.match(r"^max-[0-9]*x[0-9]*$", videomode)
        if matches != None:
            return True

    # specific resolution given
    proc = subprocess.Popen(["batocera-resolution listModes"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    for valmod in out.decode().splitlines():
        vals = valmod.split(":")
        if (videomode == vals[0]):
            return True

    eslog.error(f"invalid video mode {videomode}")
    return False


def changeMouse(mode):
    eslog.debug(f"changeMouseMode({mode})")
    if mode:
        cmd = "batocera-mouse show"
    else:
        cmd = "batocera-mouse hide"
    proc = subprocess.Popen([cmd], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()


def getGLVersion():
    try:
        # Use eglinfo since we are KMS/DRM
        if os.path.exists("/usr/bin/eglinfo") == False:
            return 0

        glxVerCmd = 'eglinfo | grep "OpenGL version"'
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
        # Use eglinfo since we are KMS/DRM
        if os.path.exists("/usr/bin/eglinfo") == False:
            return "unknown"

        glxVendCmd = 'eglinfo | grep "OpenGL vendor string"'
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
    specialFile = '/usr/share/batocera/configgen/data/special/' + systemName + '.csv'
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
