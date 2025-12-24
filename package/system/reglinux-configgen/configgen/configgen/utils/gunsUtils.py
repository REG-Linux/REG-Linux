from os import listdir, makedirs, path
from shutil import copyfile, copytree


def precalibration_copyFile(src, dst):
    if path.exists(src) and not path.exists(dst):
        if not path.exists(path.dirname(dst)):
            makedirs(path.dirname(dst))
        copyfile(src, dst)


def precalibration_copyDir(src, dst):
    if path.exists(src) and not path.exists(dst):
        if not path.exists(path.dirname(dst)):
            makedirs(path.dirname(dst))
        copytree(src, dst)


def precalibration_copyFilesInDir(srcdir, dstdir, startWith, endWith):
    for src in listdir(srcdir):
        if src.startswith(startWith):  # and src.endswith(endswith):
            precalibration_copyFile(srcdir + "/" + src, dstdir + "/" + src)


def precalibration(systemName, emulator, core, rom):
    dir = f"/usr/share/reglinux/guns-precalibrations/{systemName}"
    if not path.exists(dir):
        return
    baserom = path.basename(rom)

    if systemName == "atomiswave":
        for suffix in ["nvmem", "nvmem2"]:
            src = f"{dir}/reicast/{baserom}.{suffix}"
            dst = f"/userdata/saves/atomiswave/reicast/{baserom}.{suffix}"
            precalibration_copyFile(src, dst)

    elif systemName == "mame":
        target_dir = None
        if emulator == "mame":
            target_dir = "mame"
        elif emulator == "libretro":
            if core == "mame078plus":
                target_dir = "mame/mame2003-plus"
            elif core == "mame":
                target_dir = "mame/mame"

        if target_dir is not None:
            baserom_noext = path.splitext(baserom)[0]
            src = f"{dir}/nvram/{baserom_noext}"
            dst = f"/userdata/saves/{target_dir}/nvram/{baserom_noext}"
            precalibration_copyDir(src, dst)
            srcdir = f"{dir}/diff"
            dstdir = f"/userdata/saves/{target_dir}/diff"
            precalibration_copyFilesInDir(srcdir, dstdir, baserom_noext + "_", ".dif")

    elif systemName == "naomi":
        for suffix in ["nvmem", "eeprom"]:
            src = f"{dir}/reicast/{baserom}.{suffix}"
            dst = f"/userdata/saves/naomi/reicast/{baserom}.{suffix}"
            precalibration_copyFile(src, dst)

    elif systemName == "supermodel":
        baserom_noext = path.splitext(baserom)[0]
        src = f"{dir}/NVDATA/{baserom_noext}.nv"
        dst = f"/userdata/saves/supermodel/NVDATA/{baserom_noext}.nv"
        precalibration_copyFile(src, dst)

    elif systemName == "namco2x6":
        if emulator == "play":
            baserom_noext = path.splitext(baserom)[0]
            src = f"{dir}/play/{baserom_noext}"
            dst = f"/userdata/system/configs/play/Play Data Files/arcadesaves/{baserom_noext}.backupram"
            precalibration_copyFile(src, dst)
