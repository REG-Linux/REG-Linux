#!/usr/bin/env python3

import os
import subprocess
from utils.logger import get_logger

eslog = get_logger(__name__)

def zar_begin(rom):
    """
    Mounts a .zar archive using fuse-zar.

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
    rommountpoint = "/var/run/zar/" + os.path.basename(rom)[:-4]  # remove .zar extension

    # Ensure base /var/run/zar directory exists
    if not os.path.exists("/var/run/zar"):
        os.mkdir("/var/run/zar")

    # Try to clean up leftover mountpoint if it exists but is empty
    if os.path.exists(rommountpoint) and os.path.isdir(rommountpoint):
        eslog.debug(f"zar_begin: {rommountpoint} already exists")
        try:
            os.rmdir(rommountpoint)
        except:
            eslog.debug(f"zar_begin: failed to rmdir {rommountpoint}")
            return False, None, rommountpoint

    # Create the new mount directory
    os.mkdir(rommountpoint)

    # Mount the archive using fuse-zar
    return_code = subprocess.call(["fuse-zar", rom, rommountpoint])
    if return_code != 0:
        eslog.debug(f"zar_begin: mounting {rommountpoint} failed")
        try:
            os.rmdir(rommountpoint)
        except:
            pass
        raise Exception(f"unable to mount the file {rom} using fuse-zar")

    # Check if the archive contains a single file named like the archive
    romsingle = os.path.join(rommountpoint, os.path.basename(rom)[:-4])
    if len(os.listdir(rommountpoint)) == 1 and os.path.exists(romsingle):
        eslog.debug(f"zar: single rom {romsingle}")
        return True, rommountpoint, romsingle

    # Otherwise return the mountpoint itself
    return True, rommountpoint, rommountpoint


def zar_end(rommountpoint):
    """
    Unmounts a .zar archive mounted by zar_begin().

    This function uses fusermount to unmount the FUSE-mounted directory,
    then deletes the temporary mount directory.

    Args:
        rommountpoint (str): Path to the mounted directory.

    Raises:
        Exception: If unmounting fails.
    """
    eslog.debug(f"zar_end({rommountpoint})")

    # Unmount the FUSE filesystem
    return_code = subprocess.call(["fusermount3", "-u", rommountpoint])
    if return_code != 0:
        eslog.debug(f"zar_end: unmounting {rommountpoint} failed")
        raise Exception(f"unable to unmount the file {rommountpoint}")

    # Remove the now-empty mount directory
    os.rmdir(rommountpoint)
