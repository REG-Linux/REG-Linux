#!/usr/bin/env python3
import os
import time
import subprocess
import csv
import locale
from typing import Optional, List, Dict

from .logger import get_logger
eslog = get_logger(__name__)

def changeMode(videomode: str) -> None:
    """Set a specific video mode."""
    cmd = ["regmsg", "setMode", videomode]
    eslog.debug(f"setVideoMode({videomode}): {cmd}")
    max_tries = 2
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

def getCurrentMode() -> Optional[str]:
    try:
        proc = subprocess.Popen(["regmsg", "currentMode"], stdout=subprocess.PIPE)
        out, _ = proc.communicate()
        return out.decode().splitlines()[0] if out else None
    except Exception as e:
        eslog.error(f"Error fetching current mode: {e}")
        return None

def getScreens() -> List[str]:
    try:
        proc = subprocess.Popen(["regmsg", "listOutputs"], stdout=subprocess.PIPE)
        out, _ = proc.communicate()
        return out.decode().splitlines()
    except Exception as e:
        eslog.error(f"Error listing screens: {e}")
        return []

def getCurrentResolution(name: Optional[str] = None) -> Dict[str, int]:
    drm_mode_path = "/var/run/drmMode"

    if os.path.exists(drm_mode_path):
        try:
            with open(drm_mode_path, "r") as f:
                content = f.read().strip()
                if content:
                    vals = content.split("@")[0].split("x")
                    return {"width": int(vals[0]), "height": int(vals[1])}
        except Exception as e:
            raise ValueError(f"Error analyzing content of {drm_mode_path}: {e}")

    try:
        cmd = ["regmsg", "currentResolution"] if name is None else ["regmsg", "--screen", name, "currentResolution"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
        out, _ = proc.communicate()
        vals = out.decode().split("x")
        return {"width": int(vals[0]), "height": int(vals[1])}
    except Exception as e:
        eslog.error(f"Error getting resolution: {e}")
        return {"width": 0, "height": 0}

def getScreensInfos(config: Dict) -> List[Dict[str, int]]:
    resolution1 = getCurrentResolution()
    outputs = getScreens()

    res = [{"width": resolution1["width"], "height": resolution1["height"], "x": 0, "y": 0}]

    if "videooutput2" in config and len(outputs) > 1:
        resolution2 = getCurrentResolution(config["videooutput2"])
        res.append({"width": resolution2["width"], "height": resolution2["height"], "x": resolution1["width"], "y": 0})

        if "videooutput3" in config and len(outputs) > 2:
            resolution3 = getCurrentResolution(config["videooutput3"])
            res.append({"width": resolution3["width"], "height": resolution3["height"], "x": resolution1["width"]+resolution2["width"], "y": 0})

    eslog.debug("Screens:")
    eslog.debug(res)
    return res

def minTomaxResolution() -> None:
    subprocess.run(["regmsg", "minTomaxResolution"], stdout=subprocess.PIPE)

def getRefreshRate() -> Optional[str]:
    try:
        proc = subprocess.Popen(["regmsg", "currentRefresh"], stdout=subprocess.PIPE)
        out, _ = proc.communicate()
        return out.decode().splitlines()[0] if out else None
    except Exception as e:
        eslog.error(f"Error fetching refresh rate: {e}")
        return None

def supportSystemRotation() -> bool:
    result = subprocess.run(["regmsg", "supportSystemRotation"], stdout=subprocess.PIPE)
    return result.returncode == 0

def changeMouse(mode: bool) -> None:
    eslog.debug(f"changeMouseMode({mode})")
    cmd = "system-mouse show" if mode else "system-mouse hide"
    subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

def getGLVersion() -> float:
    try:
        if not os.path.exists("/usr/bin/glxinfo"):
            return 0.0
        glxVerCmd = 'glxinfo | grep "OpenGL version"'
        encoding = locale.getpreferredencoding(False)
        glVerOutput = subprocess.check_output(glxVerCmd, shell=True).decode(encoding)
        glVerString = glVerOutput.split()
        glVerTemp = glVerString[3].split(".")[:2]
        return float('.'.join(glVerTemp))
    except Exception as e:
        eslog.error(f"Error fetching GL version: {e}")
        return 0.0

def getGLVendor() -> str:
    try:
        if not os.path.exists("/usr/bin/glxinfo"):
            return "unknown"
        glxVendCmd = 'glxinfo | grep "OpenGL vendor string"'
        encoding = locale.getpreferredencoding(False)
        glVendOutput = subprocess.check_output(glxVendCmd, shell=True).decode(encoding)
        glVendString = glVendOutput.split()
        return glVendString[3].casefold()
    except Exception as e:
        eslog.error(f"Error fetching GL vendor: {e}")
        return "unknown"

def getAltDecoration(systemName: str, rom: str, emulator: str) -> str:
    if emulator not in ['mame', 'retroarch']:
        return "standalone"
    if systemName not in ['lynx', 'wswan', 'wswanc', 'mame', 'fbneo', 'naomi', 'atomiswave', 'nds', '3ds', 'vectrex']:
        return "0"

    specialFile = f'/usr/share/reglinux/configgen/data/special/{systemName}.csv'
    if not os.path.exists(specialFile):
        return "0"

    romName = os.path.splitext(os.path.basename(rom))[0].casefold()

    try:
        with open(specialFile, 'r') as openFile:
            specialList = csv.reader(openFile, delimiter=';')
            for row in specialList:
                if row[0].casefold() == romName:
                    return str(row[1])
    except Exception as e:
        eslog.error(f"Error reading alt decoration file: {e}")

    return "0"
