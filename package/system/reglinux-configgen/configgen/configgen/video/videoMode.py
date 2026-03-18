from contextlib import suppress
from csv import reader
from functools import lru_cache
from pathlib import Path
from subprocess import CalledProcessError, run
from time import sleep

from configgen.client import parse_regmsg_response, regmsg_send_message
from configgen.utils.logger import get_logger

# Constants
MIN_OUTPUTS_FOR_THIRD_SCREEN = 2
MIN_PARTS_FOR_VERSION_SPLIT = 2

eslog = get_logger(__name__)


def _log_regmsg_error(operation: str, error: str) -> bool:
    """Log a regmsg error and check if it's a DRM permission issue.

    Args:
        operation: The operation being performed (e.g., "setting video mode")
        error: The error message

    Returns:
        True if it's a DRM permission issue (non-fatal), False otherwise

    """
    if (
        "limited DRM rights" in error
        or "no screen detected" in error
        or "master rights" in error
    ):
        eslog.warning(f"DRM/KMS permission issue during {operation} - continuing")
        return True
    eslog.error(f"{operation}: {error}")
    return False


def changeMode(videomode: str) -> None:
    """Set a specific video mode."""
    eslog.debug(f"setVideoMode({videomode})")
    max_tries = 2
    for i in range(max_tries):
        try:
            raw_response = regmsg_send_message("setMode " + videomode)
            success, result = parse_regmsg_response(raw_response)

            if not success:
                if _log_regmsg_error("setting video mode", result):
                    return
                raise CalledProcessError(1, f"setMode {videomode}", result)

            eslog.debug(result.strip())
            return
        except CalledProcessError as e:
            if _log_regmsg_error("setting video mode", str(e.stderr)):
                return
            if i == max_tries - 1:
                raise
            sleep(1)


def getCurrentMode() -> str | None:
    try:
        raw_response = regmsg_send_message("getMode")
        success, mode = parse_regmsg_response(raw_response)

        if not success:
            _log_regmsg_error("getting current mode", mode)
            return None

        return mode
    except Exception as e:
        eslog.error(f"Error fetching current mode: {e}")
        return None


def getScreens() -> list[str]:
    """Return a list of screen names detected by regmsg."""
    try:
        raw_response = regmsg_send_message("listOutputs")
        success, result = parse_regmsg_response(raw_response)

        if not success:
            _log_regmsg_error("listing screens", result)
            return []

        if result is None:
            return []

        if isinstance(result, str):
            lines = [line.strip() for line in result.splitlines() if line.strip()]
            return lines or [result.strip()]

        return [str(result).strip()]

    except Exception as e:
        eslog.error(f"Error listing screens: {e}")
        return []


def getCurrentResolution(name: str | None = None) -> dict[str, int]:
    """Get current screen resolution.

    Args:
        name: Optional output name to query resolution for.

    Returns:
        Dictionary with 'width' and 'height' keys. Returns {'width': 0, 'height': 0} on error.

    """
    drm_mode_path = "/var/run/drmMode"

    if Path(drm_mode_path).exists():
        try:
            with Path(drm_mode_path).open(encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    vals = content.split("@")[0].split("x")
                    if len(vals) != 2:
                        eslog.error(
                            f"Invalid resolution format from {drm_mode_path}: {content}"
                        )
                        return {"width": 0, "height": 0}
                    return {"width": int(vals[0]), "height": int(vals[1])}
        except (ValueError, OSError) as e:
            eslog.error(f"Error analyzing content of {drm_mode_path}: {e}")
            return {"width": 0, "height": 0}

    try:
        out = ""
        if name is None:
            raw_response = regmsg_send_message("getResolution")
        else:
            raw_response = regmsg_send_message("getResolution --output " + name)

        # Parse the response to remove OK/ERR prefixes
        success, out = parse_regmsg_response(raw_response)

        if not success:
            eslog.error(f"Error getting resolution: {out}")
            return {"width": 0, "height": 0}

        vals = out.split("x")
        if len(vals) != 2:
            eslog.error(f"Invalid resolution format from regmsg: {out}")
            return {"width": 0, "height": 0}

        return {"width": int(vals[0]), "height": int(vals[1])}
    except (ValueError, IndexError) as e:
        eslog.error(f"Error parsing resolution: {e}")
        return {"width": 0, "height": 0}
    except Exception as e:
        eslog.error(f"Unexpected error getting resolution: {e}")
        return {"width": 0, "height": 0}


def getScreensInfos(config: dict[str, str]) -> list[dict[str, int]]:
    resolution1 = getCurrentResolution()
    outputs = getScreens()

    res = [
        {
            "width": resolution1["width"],
            "height": resolution1["height"],
            "x": 0,
            "y": 0,
        },
    ]

    if "videooutput2" in config and len(outputs) > 1:
        resolution2 = getCurrentResolution(config["videooutput2"])
        res.append(
            {
                "width": resolution2["width"],
                "height": resolution2["height"],
                "x": resolution1["width"],
                "y": 0,
            },
        )

        if "videooutput3" in config and len(outputs) > MIN_OUTPUTS_FOR_THIRD_SCREEN:
            resolution3 = getCurrentResolution(config["videooutput3"])
            res.append(
                {
                    "width": resolution3["width"],
                    "height": resolution3["height"],
                    "x": resolution1["width"] + resolution2["width"],
                    "y": 0,
                },
            )

    eslog.debug("Screens:")
    eslog.debug(res)
    return res


def minTomaxResolution() -> None:
    try:
        raw_response = regmsg_send_message("minToMaxResolution")
        success, result = parse_regmsg_response(raw_response)

        if not success:
            eslog.error(f"Error calling minToMaxResolution: {result}")
            # Check if this is a DRM permission issue and log appropriately
            if "limited DRM rights" in result or "no screen detected" in result:
                eslog.warning(
                    "DRM/KMS permission issue detected - continuing without resolution change",
                )
    except Exception as e:
        eslog.error(f"Exception in minToMaxResolution: {e}")
        # Check if this is a DRM permission issue
        if "DRM" in str(e) or "master rights" in str(e):
            eslog.warning(
                "DRM/KMS permission issue detected - continuing without resolution change",
            )


def getRefreshRate() -> str | None:
    try:
        raw_response = regmsg_send_message("getRefresh")
        success, out = parse_regmsg_response(raw_response)

        if not success:
            eslog.error(f"Error getting refresh rate: {out}")
            return None

        if out:
            return out.splitlines()[0]
        return None
    except Exception as e:
        eslog.error(f"Error fetching refresh rate: {e}")
        return None


def supportSystemRotation() -> bool:
    try:
        raw_response = regmsg_send_message("screen supportSystemRotation")
        success, result = parse_regmsg_response(raw_response)

        if not success:
            eslog.error(f"Error checking for system rotation support: {result}")
            return False

        return result.strip().lower() == "true"
    except Exception as e:
        eslog.error(f"Error checking for system rotation support: {e}")
        return False


def changeMouse(mode: bool) -> None:
    eslog.debug(f"changeMouseMode({mode})")
    cmd = "system-mouse show" if mode else "system-mouse hide"
    try:
        run(cmd, check=False, shell=True, capture_output=True)
    except Exception as e:
        eslog.warning(f"Failed to change mouse visibility: {e}")
        # Don't raise an error for mouse visibility issues


@lru_cache(maxsize=1)
def _get_eglinfo_cached() -> tuple[str, float]:
    """Get GL vendor and version in a single eglinfo call (cached).

    Returns:
        Tuple of (vendor_string, version_float)

    """
    lines = _get_eglinfo_lines()
    vendor = "unknown"
    version = 0.0

    for line in lines:
        if "OpenGL vendor" in line:
            parts = line.split(":", 1)
            if len(parts) >= 2:
                vendor = parts[1].strip().split()[0].casefold()
        elif "OpenGL version" in line:
            parts = line.split(":", 1)
            if len(parts) >= 2:
                version_token = parts[1].strip().split()[0]
                glVerTemp = version_token.split(".")[:2]
                with suppress(ValueError, TypeError):
                    version = float(".".join(glVerTemp))

    return vendor, version


def getGLVersion() -> float:
    """Get OpenGL version (cached)."""
    return _get_eglinfo_cached()[1]


def getGLVendor() -> str:
    """Get OpenGL vendor string (cached)."""
    return _get_eglinfo_cached()[0]


def _get_eglinfo_lines() -> list[str]:
    eglinfo_path = "/usr/bin/eglinfo"
    if not Path(eglinfo_path).exists():
        return []

    try:
        result = run([eglinfo_path], capture_output=True, text=True, check=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except CalledProcessError as e:
        eslog.error(
            f"Error running {eglinfo_path}: {e.stderr.strip() if e.stderr else e}",
        )
        return []
    except FileNotFoundError:
        return []


def getAltDecoration(systemName: str, rom: str, emulator: str) -> str:
    if emulator not in {"mame", "retroarch"}:
        return "standalone"
    if systemName not in {
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
    }:
        return "0"

    specialFile = f"/usr/share/reglinux/configgen/data/special/{systemName}.csv"
    if not Path(specialFile).exists():
        return "0"

    romName = Path(rom).stem.casefold()

    try:
        with Path(specialFile).open(encoding="utf-8") as openFile:
            specialList = reader(openFile, delimiter=";")
            for row in specialList:
                if len(row) >= 2 and row[0].casefold() == romName:
                    return str(row[1])
    except Exception as e:
        eslog.error(f"Error reading alt decoration file: {e}")

    return "0"
