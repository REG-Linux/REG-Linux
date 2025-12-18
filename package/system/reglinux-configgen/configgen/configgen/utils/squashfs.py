import os
import subprocess
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


def squashfs_begin(rom):
    eslog.debug(f"squashfs_begin({rom})")
    rommountpoint = "/var/run/squashfs/" + os.path.basename(rom)[:-9]

    if not os.path.exists("/var/run/squashfs"):
        os.mkdir("/var/run/squashfs")

    # first, try to clean an empty remaining directory (for example because of a crash)
    if os.path.exists(rommountpoint) and os.path.isdir(rommountpoint):
        eslog.debug(f"squashfs_begin: {rommountpoint} already exists")
        # try to remove an empty directory, else, run the directory, ignoring the .squashfs
        try:
            os.rmdir(rommountpoint)
        except (OSError, FileNotFoundError) as e:
            eslog.debug(f"squashfs_begin: failed to rmdir {rommountpoint} - {str(e)}")
            return False, None, rommountpoint

    # ok, the base directory doesn't exist, let's create it and mount the squashfs on it
    os.mkdir(rommountpoint)
    return_code = subprocess.call(["mount", rom, rommountpoint])
    if return_code != 0:
        eslog.debug(f"squashfs_begin: mounting {rommountpoint} failed")
        try:
            os.rmdir(rommountpoint)
        except (OSError, FileNotFoundError) as e:
            eslog.debug(
                f"squashfs: failed to remove directory {rommountpoint} - {str(e)}"
            )
            pass
        raise Exception(f"unable to mount the file {rom}")

    # if the squashfs contains a single file with the same name, take it as the rom file
    romsingle = rommountpoint + "/" + os.path.basename(rom)[:-9]
    if len(os.listdir(rommountpoint)) == 1 and os.path.exists(romsingle):
        eslog.debug(f"squashfs: single rom {romsingle}")
        return True, rommountpoint, romsingle

    return True, rommountpoint, rommountpoint


def squashfs_end(rommountpoint):
    eslog.debug(f"squashfs_end({rommountpoint})")

    # umount
    return_code = subprocess.call(["umount", rommountpoint])
    if return_code != 0:
        eslog.debug(f"squashfs_begin: unmounting {rommountpoint} failed")
        raise Exception(f"unable to umount the file {rommountpoint}")

    # cleaning the empty directory
    os.rmdir(rommountpoint)
