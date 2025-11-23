from os import path
from time import sleep
from subprocess import PIPE, CalledProcessError, run, check_output
from csv import reader
from sys import stdout
from typing import Optional, List, Dict
from .logger import get_logger

from .regmsgclient import regmsg_send_message

eslog = get_logger(__name__)


def changeMode(videomode: str) -> None:
    """Set a specific video mode."""
    eslog.debug(f"setVideoMode({videomode})")
    max_tries = 2
    for i in range(max_tries):
        try:
            result = regmsg_send_message("setMode " + videomode)
            eslog.debug(result.strip())
            return
        except CalledProcessError as e:
            eslog.error(f"Error setting video mode: {e.stderr}")
            if i == max_tries - 1:
                raise
            sleep(1)


def getCurrentMode() -> Optional[str]:
    try:
        return regmsg_send_message("getMode")
    except Exception as e:
        eslog.error(f"Error fetching current mode: {e}")
        return None


def getScreens() -> List[str]:
    """Return a list of screen names detected by regmsg."""
    try:
        result = regmsg_send_message("listOutputs")

        if result is None:
            return []

        if isinstance(result, str):
            lines = [line.strip() for line in result.splitlines() if line.strip()]
            return lines if lines else [result.strip()]

        return [str(result).strip()]

    except Exception as e:
        eslog.error(f"Error listing screens: {e}")
        return []


def getCurrentResolution(name: Optional[str] = None) -> Dict[str, int]:
    drm_mode_path = "/var/run/drmMode"

    if path.exists(drm_mode_path):
        try:
            with open(drm_mode_path, "r") as f:
                content = f.read().strip()
                if content:
                    vals = content.split("@")[0].split("x")
                    return {"width": int(vals[0]), "height": int(vals[1])}
        except Exception as e:
            raise ValueError(f"Error analyzing content of {drm_mode_path}: {e}")

    try:
        out = ""
        if name is None:
            out = regmsg_send_message("getResolution")
        else:
            out = regmsg_send_message("getResolution --output " + name)
        vals = out.split("x")
        return {"width": int(vals[0]), "height": int(vals[1])}
    except Exception as e:
        eslog.error(f"Error getting resolution: {e}")
        return {"width": 0, "height": 0}


def getScreensInfos(config: Dict) -> List[Dict[str, int]]:
    resolution1 = getCurrentResolution()
    outputs = getScreens()

    res = [
        {"width": resolution1["width"], "height": resolution1["height"], "x": 0, "y": 0}
    ]

    if "videooutput2" in config and len(outputs) > 1:
        resolution2 = getCurrentResolution(config["videooutput2"])
        res.append(
            {
                "width": resolution2["width"],
                "height": resolution2["height"],
                "x": resolution1["width"],
                "y": 0,
            }
        )

        if "videooutput3" in config and len(outputs) > 2:
            resolution3 = getCurrentResolution(config["videooutput3"])
            res.append(
                {
                    "width": resolution3["width"],
                    "height": resolution3["height"],
                    "x": resolution1["width"] + resolution2["width"],
                    "y": 0,
                }
            )

    eslog.debug("Screens:")
    eslog.debug(res)
    return res


def minTomaxResolution() -> None:
    regmsg_send_message("minToMaxResolution")


def getRefreshRate() -> Optional[str]:
    try:
        out = regmsg_send_message("getRefresh")
        if out:
            return out.splitlines()[0]
        else:
            return None
    except Exception as e:
        eslog.error(f"Error fetching refresh rate: {e}")
        return None


def supportSystemRotation() -> bool:
    result = run(["regmsg screen", "supportSystemRotation"], stdout=PIPE)
    return result.returncode == 0


def changeMouse(mode: bool) -> None:
    eslog.debug(f"changeMouseMode({mode})")
    cmd = "system-mouse show" if mode else "system-mouse hide"
    run(cmd, shell=True, stdout=PIPE)


def getGLVersion():
    try:
        # Use eglinfo since we are KMS/DRM
        if not path.exists("/usr/bin/eglinfo"):
            return 0

        glxVerCmd = 'eglinfo | grep "OpenGL version"'
        glVerOutput = check_output(glxVerCmd, shell=True).decode(stdout.encoding)
        glVerString = glVerOutput.split()
        glVerTemp = glVerString[3].split(".")
        if len(glVerTemp) > 2:
            del glVerTemp[2:]
        glVersion = float(".".join(glVerTemp))
        return glVersion
    except (ValueError, TypeError, CalledProcessError):
        return 0


def getGLVendor():
    try:
        # Use eglinfo since we are KMS/DRM
        if not path.exists("/usr/bin/eglinfo"):
            return "unknown"

        glxVendCmd = 'eglinfo | grep "OpenGL vendor string"'
        glVendOutput = check_output(glxVendCmd, shell=True).decode(stdout.encoding)
        glVendString = glVendOutput.split()
        glVendor = glVendString[3].casefold()
        return glVendor
    except (CalledProcessError, IndexError, AttributeError):
        return "unknown"


def getAltDecoration(systemName: str, rom: str, emulator: str) -> str:
    if emulator not in ["mame", "retroarch"]:
        return "standalone"
    if systemName not in [
        "lynx",
        "wswan",
        "wswanc",
        "mame",
        "fbneo",
        "naomi",
        "atomiswave",
        "nds",
        "3ds",
        "vectrex",
    ]:
        return "0"

    specialFile = f"/usr/share/reglinux/configgen/data/special/{systemName}.csv"
    if not path.exists(specialFile):
        return "0"

    romName = path.splitext(path.basename(rom))[0].casefold()

    try:
        with open(specialFile, "r") as openFile:
            specialList = reader(openFile, delimiter=";")
            for row in specialList:
                if row[0].casefold() == romName:
                    return str(row[1])
    except Exception as e:
        eslog.error(f"Error reading alt decoration file: {e}")

    return "0"
