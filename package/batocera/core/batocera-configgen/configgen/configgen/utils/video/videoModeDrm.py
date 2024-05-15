#!/usr/bin/env python
import csv
import glob
import os
import re
import subprocess
import sys
import time

from utils.logger import get_logger

eslog = get_logger(__name__)

drmModes = []

# Set a specific video mode
def drmChangeMode(videomode):
    if drmCheckModeExists(videomode):
        drmSetMode(videomode)

def drmSetMode(videomode):
    eslog.debug(f"drmSetMode({videomode})")
    max_tries = 2  # maximum number of tries to set the mode
    for i in range(max_tries):
        try:
            # max resolution given
            if videomode[0:4] == "max-":
                matches = re.match(r"^max-[0-9]*x[0-9]*$", videomode)
                if matches != None:
                    videomode =re.sub("max-","",videomode)
                    drmMinTomaxResolution(videomode)
                else:  # normal mode
                    # check that the mode is valid
                    modes = drmListModes()
                    for mode in modes:
                        if re.match("^$"+videomode+":", mode):
                            file = open("/var/run/drmMode", "w")
                            file.write(mode.split(".")[1])
                            file.close()
                            return
                    eslog.debug(f"invalid mode ({videomode})")
        except subprocess.CalledProcessError as e:
            eslog.error(f"Error setting video mode: {e.stderr}")
            if i == max_tries - 1:
                raise
            time.sleep(1)

def drmGetCurrentMode():
    #f_checkVals

    drm_conn = open("/var/run/drmConn", 'r')
    connector = int(drm_conn.readline())
    drm_conn.close()

    drm_mode = open("/var/run/drmMode", 'r')
    current_mode = int(drm_mode.readline())
    drm_mode.close()

    modes = drmListModes()
    for mode in modes:
        if re.match(r"^"+str(connector)+"\."+str(current_mode)+"\.", mode):
            return mode.split(":")[0]

def drmGetScreensInfos(config):
    resolution1 = drmGetCurrentResolution()
    outputs = drmGetScreens()

    res = []
    res.append({"width": resolution1["width"], "height": resolution1["height"], "x": 0, "y": 0})

    if "videooutput2" not in config or len(outputs) <= 1:
        eslog.debug("Screens:")
        eslog.debug(res)
        return res

    resolution2 = drmGetCurrentResolution(config["videooutput2"])
    res.append({"width": resolution2["width"], "height": resolution2["height"], "x": resolution1["width"], "y": 0})

    if "videooutput3" not in config or len(outputs) <= 2:
        eslog.debug("Screens:")
        eslog.debug(res)
        return res

    resolution3 = drmGetCurrentResolution(config["videooutput3"])
    res.append({"width": resolution3["width"], "height": resolution3["height"], "x": resolution1["width"]+resolution2["width"], "y": 0})

    eslog.debug("Screens:")
    eslog.debug(res)
    return res

def drmGetScreens():
    proc = subprocess.Popen(["batocera-resolution listOutputs"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return out.decode().splitlines()

def drmMinTomaxResolution(videomode):
    current = drmGetCurrentResolution()
    width = videomode.split("x")[0]
    height = videomode.split("x")[1]
    # Clamp to 1920x1080 because of 4K TVs
    if int(width) > 1920:
        width = 1920
    if int(height) > 1080:
        height = 1080
    maxWidth = int(width)
    maxHeight = int(height)
    if int(current["width"]) < maxWidth and int(current["height"]) < maxHeight:
        # TODO arch rpi4 refuses 1360x768
        # ARCH =$(cat / usr / share / batocera / batocera.arch)
        # if ! test "${ARCH}" = "bcm2711" -a "${CURRENTWIDTH}" = 1360 -a "${CURRENTHEIGHT}" = 768
        # exit 0
        return

    modes = drmListModes()
    # TODO implement this..
    #sed - e "/i)$/!" s + ")$" + "p)" + -e s + "^\([^:]*\):[^ ]* \([0-9]*x[0-9]*\) \([0-9]*\)Hz (\(.*\))$" + "\2_\3_\4:\1:\2" + | sort - nr | sed - e "s/_[0-9]*x[0-9]*[pi]//" |
    #while IFS=':\n' read SORTSTR SUGGMODE SUGGRESOLUTION
    #do
    #SUGGWIDTH =$(echo "${SUGGRESOLUTION}" | cut -d x -f 1)
    #SUGGHEIGHT =$(echo "${SUGGRESOLUTION}" | cut -d x -f 2)

    #if test "${SUGGWIDTH}" -le "${MAXWIDTH}" -a "${SUGGHEIGHT}" -le "${MAXHEIGHT}"
    #then
    #echo "${SUGGMODE}" | cut - d "." - f 2 > / var / run / drmMode
    #exit 0

def drmGetCurrentResolution(name = None):
    if name is None:
        drm_conn = open("/var/run/drmConn", 'r')
        connector = int(drm_conn.readline())
        drm_conn.close()

        drm_mode = open("/var/run/drmMode", 'r')
        current_mode = int(drm_mode.readline())
        drm_mode.close()

        eslog.debug("drmGetCurrentResolution")
        modes = drmListModes()
        for mode in modes:
            if re.match(r"^" + str(connector) + r"\." + str(current_mode) + r"\.", mode):
                resolution = re.sub(r"^[^:]*:[^ ]* ([0-9]*x[0-9]*) .*$", r"\1", mode)
                width = resolution.split('x')[0]
                height = resolution.split('x')[1]
                return { "width": int(width), "height": int(height) }
    else:
        proc = subprocess.Popen(["batocera-resolution --screen {} currentResolution".format(name)], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        vals = out.decode().split("x")
        return { "width": int(vals[0]), "height": int(vals[1]) }

def drmSupportSystemRotation():
    proc = subprocess.Popen(["batocera-resolution supportSystemRotation"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return proc.returncode == 0

def drmCheckModeExists(videomode):
    # max resolution given
    if videomode[0:4] == "max-":
        matches = re.match(r"^max-[0-9]*x[0-9]*$", videomode)
        if matches is not None:
            return True

    modes = drmListModes()

    # specific resolution given
    for mode in modes:
        v = mode.split(":")
        if videomode == v[0]:
            return True

    eslog.error(f"invalid video mode {videomode}")
    return False

def drmListModes():
    if drmModes:
        return drmModes

    drm_conn = open("/var/run/drmConn")
    connector = int(drm_conn.readline())
    drm_conn.close()

    drmModes.clear()
    drmModes.append("max-1920x1080:maximum 1920x1080")
    drmModes.append("max-640x480:maximum 640x480")

    gpus = glob.glob("/dev/dri/card*")
    for gpu in gpus:
        proc = subprocess.Popen(["batocera-drminfo" + " " + gpu + " all"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        for line in out.decode().splitlines():
            if re.match(r'^'+str(connector)+r'\.', line):
                mode = re.sub(r"^([0-9]*)\.([0-9]*):([^ ]*) ([0-9]*)x([0-9]*) ([0-9]*)(Hz .*)$",r"\1.\2.\4x\5.\6:\3 \4x\5 \6\7", line)
                drmModes.append(mode)

    return drmModes
