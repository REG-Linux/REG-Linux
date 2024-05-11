#!/usr/bin/env python
import csv
import os
import re
import subprocess
import sys
import time

from utils.logger import get_logger

eslog = get_logger(__name__)

# Set a specific video mode
def waylandChangeMode(videomode):
    if waylandCheckModeExists(videomode):
        cmd = ["batocera-resolution", "setMode", videomode]
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

def waylandGetCurrentMode():
    proc = subprocess.Popen(["batocera-resolution currentMode"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    for val in out.decode().splitlines():
        return val # return the first line

def waylandGetScreensInfos(config):
    resolution1 = waylandGetCurrentResolution()
    outputs = waylandGetScreens()

    res = []
    res.append({"width": resolution1["width"], "height": resolution1["height"], "x": 0, "y": 0})

    if "videooutput2" not in config or len(outputs) <= 1:
        eslog.debug("Screens:")
        eslog.debug(res)
        return res

    resolution2 = waylandGetCurrentResolution(config["videooutput2"])
    res.append({"width": resolution2["width"], "height": resolution2["height"], "x": resolution1["width"], "y": 0})

    if "videooutput3" not in config or len(outputs) <= 2:
        eslog.debug("Screens:")
        eslog.debug(res)
        return res

    resolution3 = waylandGetCurrentResolution(config["videooutput3"])
    res.append({"width": resolution3["width"], "height": resolution3["height"], "x": resolution1["width"]+resolution2["width"], "y": 0})

    eslog.debug("Screens:")
    eslog.debug(res)
    return res

def waylandGetScreens():
    proc = subprocess.Popen(["batocera-resolution listOutputs"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return out.decode().splitlines()

def waylandMinTomaxResolution():
    proc = subprocess.Popen(["batocera-resolution minTomaxResolution"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()

def waylandGetCurrentResolution(name = None):
    if name is None:
        proc = subprocess.Popen(["batocera-resolution currentResolution"], stdout=subprocess.PIPE, shell=True)
    else:
        proc = subprocess.Popen(["batocera-resolution --screen {} currentResolution".format(name)], stdout=subprocess.PIPE, shell=True)

    (out, err) = proc.communicate()
    vals = out.decode().split("x")
    return { "width": int(vals[0]), "height": int(vals[1]) }

def waylandSupportSystemRotation():
    proc = subprocess.Popen(["batocera-resolution supportSystemRotation"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    return proc.returncode == 0

def waylandCheckModeExists(videomode):
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
        if(videomode == vals[0]):
            return True

    eslog.error(f"invalid video mode {videomode}")
    return False
