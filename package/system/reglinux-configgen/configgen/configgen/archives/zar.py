"""Utility module for handling zar archives in RegLinux."""

import shutil
from pathlib import Path
from subprocess import TimeoutExpired, call
from typing import Any

from configgen.core.exceptions import ArchiveMountError
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


def zar_begin(rom: str) -> tuple[bool, str | None, Any]:
    """Mounts a .zar archive using fuse-zar.

    This function creates a temporary mount point under /var/run/zar/,
    attempts to mount the given .zar file using fuse-zar, and checks if
    it contains a single ROM file matching the archive name.

    Args:
        rom (str): Path to the .zar archive.

    Returns:
        tuple: (need_end, mountpoint, rompath)
            - need_end (bool): Indicates whether zar_end() should be called later.
            - mountpoint (str): Path to the mounted directory.
            - rompath (str): Full path to the ROM file inside the archive or the mountpoint itself.

    Raises:
        Exception: If mounting fails.

    """
    eslog.debug(f"zar_begin({rom})")

    # Define the mount point based on the archive name
    rommountpoint = str(
        Path("/var/run/zar") / Path(rom).name[:-4],
    )  # remove .zar extension

    # Ensure base /var/run/zar directory exists
    zar_dir = Path("/var/run/zar")
    if not zar_dir.exists():
        zar_dir.mkdir(parents=True, exist_ok=True)

    # Try to clean up leftover mountpoint if it exists but is empty
    mountpoint_path = Path(rommountpoint)
    if mountpoint_path.exists() and mountpoint_path.is_dir():
        eslog.debug(f"zar_begin: {rommountpoint} already exists")
        try:
            mountpoint_path.rmdir()
        except (OSError, FileNotFoundError) as e:
            eslog.debug(f"zar_begin: failed to rmdir {rommountpoint} - {e!s}")
            return False, None, rommountpoint

    # Create the new mount directory
    mountpoint_path.mkdir(parents=True, exist_ok=True)

    # Mount the archive using fuse-zar
    try:
        return_code = call(["fuse-zar", rom, rommountpoint], timeout=30)
    except TimeoutExpired:
        eslog.error(f"fuse-zar mount timed out after 30s for {rom}")
        shutil.rmtree(rommountpoint, ignore_errors=True)
        raise ArchiveMountError(rom, operation="mount (timeout)") from None
    if return_code != 0:
        eslog.debug(f"zar_begin: mounting {rommountpoint} failed")
        try:
            # Use shutil.rmtree for robust cleanup of potentially non-empty directories
            shutil.rmtree(rommountpoint, ignore_errors=True)
        except (OSError, FileNotFoundError) as e:
            eslog.debug(f"zar: failed to remove directory {rommountpoint} - {e!s}")
        raise ArchiveMountError(rom, operation="mount")

    # Check if the archive contains a single file named like the archive
    romsingle = str(Path(rommountpoint) / Path(rom).name[:-4])
    if len(list(Path(rommountpoint).iterdir())) == 1 and Path(romsingle).exists():
        eslog.debug(f"zar: single rom {romsingle}")
        return True, rommountpoint, romsingle

    # Otherwise return the mountpoint itself
    return True, rommountpoint, rommountpoint


def zar_end(rommountpoint: str) -> bool:
    """Unmounts a .zar archive mounted by zar_begin().

    This function uses fusermount to unmount the FUSE-mounted directory,
    then deletes the temporary mount directory.

    Args:
        rommountpoint (str): Path to the mounted directory.

    Raises:
        Exception: If unmounting fails.

    """
    eslog.debug(f"zar_end({rommountpoint})")

    # Unmount the FUSE filesystem
    try:
        return_code = call(["fusermount3", "-u", rommountpoint], timeout=30)
    except TimeoutExpired:
        eslog.error(f"fusermount3 unmount timed out after 30s for {rommountpoint}")
        raise ArchiveMountError(rommountpoint, operation="unmount (timeout)") from None
    if return_code != 0:
        eslog.debug(f"zar_end: unmounting {rommountpoint} failed")
        raise ArchiveMountError(rommountpoint, operation="unmount")

    # Remove the now-empty mount directory with robust cleanup
    try:
        shutil.rmtree(rommountpoint, ignore_errors=True)
    except (OSError, FileNotFoundError) as e:
        eslog.debug(f"zar_end: failed to remove directory {rommountpoint} - {e!s}")
        raise
    return True
