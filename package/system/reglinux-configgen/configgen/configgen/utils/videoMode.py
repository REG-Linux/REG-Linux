from csv import reader
from os import path
from subprocess import PIPE, CalledProcessError, run
from time import sleep

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


def getCurrentMode() -> str | None:
    try:
        return regmsg_send_message("getMode")
    except Exception as e:
        eslog.error(f"Error fetching current mode: {e}")
        return None


def getScreens() -> list[str]:
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


def getCurrentResolution(name: str | None = None) -> dict[str, int]:
    drm_mode_path = "/var/run/drmMode"

    if path.exists(drm_mode_path):
        try:
            with open(drm_mode_path) as f:
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


def getScreensInfos(config: dict[str, str]) -> list[dict[str, int]]:
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


def getRefreshRate() -> str | None:
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


def getGLVersion() -> float:
    lines = _get_eglinfo_lines()
    for line in lines:
        if "OpenGL version" not in line:
            continue
        parts = line.split(":", 1)
        if len(parts) < 2:
            continue
        version_token = parts[1].strip().split()[0]
        glVerTemp = version_token.split(".")
        if len(glVerTemp) > 2:
            glVerTemp = glVerTemp[:2]
        try:
            return float(".".join(glVerTemp))
        except (ValueError, TypeError):
            return 0
    return 0


def getGLVendor() -> str:
    lines = _get_eglinfo_lines()
    for line in lines:
        if "OpenGL vendor" not in line:
            continue
        parts = line.split(":", 1)
        if len(parts) < 2:
            continue
        vendor_token = parts[1].strip().split()[0]
        return vendor_token.casefold()
    return "unknown"


def _get_eglinfo_lines() -> list[str]:
    eglinfo_path = "/usr/bin/eglinfo"
    if not path.exists(eglinfo_path):
        return []

    try:
        result = run([eglinfo_path], stdout=PIPE, stderr=PIPE, text=True, check=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except CalledProcessError as e:
        eslog.error(f"Error running {eglinfo_path}: {e.stderr.strip() if e.stderr else e}")
        return []
    except FileNotFoundError:
        return []


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
        with open(specialFile) as openFile:
            specialList = reader(openFile, delimiter=";")
            for row in specialList:
                if row[0].casefold() == romName:
                    return str(row[1])
    except Exception as e:
        eslog.error(f"Error reading alt decoration file: {e}")

    return "0"
