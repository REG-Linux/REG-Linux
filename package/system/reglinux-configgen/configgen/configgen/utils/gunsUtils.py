from os import listdir
from pathlib import Path
from shutil import copyfile, copytree


def precalibration_copyFile(src: str, dst: str) -> None:
    src_path = Path(src)
    dst_path = Path(dst)
    if src_path.exists() and not dst_path.exists():
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        copyfile(str(src_path), str(dst_path))


def precalibration_copyDir(src: str, dst: str) -> None:
    src_path = Path(src)
    dst_path = Path(dst)
    if src_path.exists() and not dst_path.exists():
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        copytree(str(src_path), str(dst_path))


def precalibration_copyFilesInDir(
    srcdir: str, dstdir: str, startWith: str, endWith: str,
) -> None:
    srcdir_path = Path(srcdir)
    dstdir_path = Path(dstdir)
    for src in listdir(str(srcdir_path)):
        if src.startswith(startWith):  # and src.endswith(endswith):
            precalibration_copyFile(str(srcdir_path / src), str(dstdir_path / src))


def precalibration(systemName: str, emulator: str, core: str, rom: str) -> None:
    dir_path = Path("/usr/share/reglinux/guns-precalibrations") / systemName
    if not dir_path.exists():
        return
    baserom = Path(rom).name

    if systemName == "atomiswave":
        for suffix in ["nvmem", "nvmem2"]:
            src = str(dir_path / "reicast" / f"{baserom}.{suffix}")
            dst = str(
                Path("/userdata/saves/atomiswave/reicast") / f"{baserom}.{suffix}",
            )
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
            baserom_noext = Path(baserom).stem
            src = str(dir_path / "nvram" / baserom_noext)
            dst = str(Path("/userdata/saves") / target_dir / "nvram" / baserom_noext)
            precalibration_copyDir(src, dst)
            srcdir = str(dir_path / "diff")
            dstdir = str(Path("/userdata/saves") / target_dir / "diff")
            precalibration_copyFilesInDir(srcdir, dstdir, baserom_noext + "_", ".dif")

    elif systemName == "naomi":
        for suffix in ["nvmem", "eeprom"]:
            src = str(dir_path / "reicast" / f"{baserom}.{suffix}")
            dst = str(Path("/userdata/saves/naomi/reicast") / f"{baserom}.{suffix}")
            precalibration_copyFile(src, dst)

    elif systemName == "supermodel":
        baserom_noext = Path(baserom).stem
        src = str(dir_path / "NVDATA" / f"{baserom_noext}.nv")
        dst = str(Path("/userdata/saves/supermodel/NVDATA") / f"{baserom_noext}.nv")
        precalibration_copyFile(src, dst)

    elif systemName == "namco2x6" and emulator == "play":
        baserom_noext = Path(baserom).stem
        src = str(dir_path / "play" / baserom_noext)
        dst = str(
            Path("/userdata/system/configs/play/Play Data Files/arcadesaves")
            / f"{baserom_noext}.backupram",
        )
        precalibration_copyFile(src, dst)
