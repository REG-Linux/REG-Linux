"""Utility module for handling squashfs archives in RegLinux."""

import subprocess
from pathlib import Path
from subprocess import TimeoutExpired
from typing import Any

from configgen.core.exceptions import ArchiveMountError
from configgen.utils.logger import get_logger

eslog = get_logger(__name__)


def squashfs_begin(rom: str) -> tuple[bool, str | None, Any]:
    """Mount a squashfs archive.

    Args:
        rom: Path to the .squashfs archive.

    Returns:
        tuple: (need_end, mountpoint, rompath)
            - need_end (bool): Indicates whether squashfs_end() should be called later.
            - mountpoint (str): Path to the mounted directory.
            - rompath (str): Full path to the ROM file inside the archive or the mountpoint itself.

    Raises:
        Exception: If mounting fails.

    """
    eslog.debug(f"squashfs_begin({rom})")
    rom_path = Path(rom)
    rommountpoint = Path("/var/run/squashfs") / rom_path.name[:-9]

    squashfs_dir = Path("/var/run/squashfs")
    if not squashfs_dir.exists():
        squashfs_dir.mkdir(parents=True, exist_ok=True)

    # first, try to clean an empty remaining directory (for example because of a crash)
    if rommountpoint.exists() and rommountpoint.is_dir():
        eslog.debug(f"squashfs_begin: {rommountpoint} already exists")
        # try to remove an empty directory, else, run the directory, ignoring the .squashfs
        try:
            rommountpoint.rmdir()
        except (OSError, FileNotFoundError) as e:
            eslog.debug(f"squashfs_begin: failed to rmdir {rommountpoint} - {e!s}")
            return False, None, str(rommountpoint)

    # ok, the base directory doesn't exist, let's create it and mount the squashfs on it
    rommountpoint.mkdir(parents=True, exist_ok=True)
    try:
        return_code = subprocess.call(["mount", rom, str(rommountpoint)], timeout=30)
    except TimeoutExpired:
        eslog.error(f"mount squashfs timed out after 30s for {rom}")
        rommountpoint.rmdir()
        raise ArchiveMountError(rom, operation="mount (timeout)") from None
    if return_code != 0:
        eslog.debug(f"squashfs_begin: mounting {rommountpoint!s} failed")
        try:
            rommountpoint.rmdir()
        except (OSError, FileNotFoundError) as e:
            eslog.debug(
                f"squashfs: failed to remove directory {rommountpoint} - {e!s}",
            )
        raise ArchiveMountError(rom, operation="mount")

    # if the squashfs contains a single file with the same name, take it as the rom file
    romsingle = rommountpoint / rom_path.name[:-9]
    if len(list(rommountpoint.iterdir())) == 1 and romsingle.exists():
        eslog.debug(f"squashfs: single rom {romsingle}")
        return True, str(rommountpoint), str(romsingle)

    return True, str(rommountpoint), str(rommountpoint)


def squashfs_end(rommountpoint: str) -> bool:
    """Unmount a squashfs archive.

    Args:
        rommountpoint: Path to the mounted directory.

    Returns:
        bool: True if unmount successful.

    Raises:
        ArchiveMountError: If unmounting fails.

    """
    eslog.debug(f"squashfs_end({rommountpoint})")

    # umount
    try:
        return_code = subprocess.call(["umount", rommountpoint], timeout=30)
    except TimeoutExpired:
        eslog.error(f"umount squashfs timed out after 30s for {rommountpoint}")
        raise ArchiveMountError(rommountpoint, operation="unmount (timeout)") from None
    if return_code != 0:
        eslog.debug(f"squashfs_begin: unmounting {rommountpoint} failed")
        raise ArchiveMountError(rommountpoint, operation="unmount")

    # cleaning the empty directory
    Path(rommountpoint).rmdir()
    return True
