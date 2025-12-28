import subprocess
from pathlib import Path
from typing import Any

from configgen.utils.logger import get_logger

eslog = get_logger(__name__)

# Example of how it was used
# def main(args, maxnbplayers):
#    # squashfs roms if squashed
#    extension = os.path.splitext(args.rom)[1][1:].lower()
#    if extension == "squashfs":
#        exitCode = 0
#        need_end = False
#        try:
#            need_end, rommountpoint, rom = squashfs.squashfs_begin(args.rom)
#            exitCode = start_rom(args, maxnbplayers, rom, args.rom)
#        finally:
#            if need_end:
#                squashfs.squashfs_end(rommountpoint)
#        return exitCode
#    else:
#        return start_rom(args, maxnbplayers, args.rom, args.rom)


def squashfs_begin(rom: str) -> tuple[bool, str | None, Any]:
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
            eslog.debug(f"squashfs_begin: failed to rmdir {rommountpoint} - {str(e)}")
            return False, None, str(rommountpoint)

    # ok, the base directory doesn't exist, let's create it and mount the squashfs on it
    rommountpoint.mkdir(parents=True, exist_ok=True)
    return_code = subprocess.call(["mount", rom, str(rommountpoint)])
    if return_code != 0:
        eslog.debug(f"squashfs_begin: mounting {str(rommountpoint)} failed")
        try:
            rommountpoint.rmdir()
        except (OSError, FileNotFoundError) as e:
            eslog.debug(
                f"squashfs: failed to remove directory {rommountpoint} - {str(e)}"
            )
            pass
        raise Exception(f"unable to mount the file {rom}")

    # if the squashfs contains a single file with the same name, take it as the rom file
    romsingle = rommountpoint / rom_path.name[:-9]
    if len(list(rommountpoint.iterdir())) == 1 and romsingle.exists():
        eslog.debug(f"squashfs: single rom {romsingle}")
        return True, str(rommountpoint), str(romsingle)

    return True, str(rommountpoint), str(rommountpoint)


def squashfs_end(rommountpoint: str) -> bool:
    eslog.debug(f"squashfs_end({rommountpoint})")

    # umount
    return_code = subprocess.call(["umount", rommountpoint])
    if return_code != 0:
        eslog.debug(f"squashfs_begin: unmounting {rommountpoint} failed")
        raise Exception(f"unable to umount the file {rommountpoint}")

    # cleaning the empty directory
    Path(rommountpoint).rmdir()
    return True
