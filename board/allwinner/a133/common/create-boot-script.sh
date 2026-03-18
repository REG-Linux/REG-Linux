#!/bin/bash

# HOST_DIR = host dir
# BOARD_DIR = board specific dir
# BUILD_DIR = base dir/build
# BINARIES_DIR = images dir
# TARGET_DIR = target dir
# REGLINUX_BINARIES_DIR = reglinux binaries sub directory

HOST_DIR=$1
BOARD_DIR=$2
BUILD_DIR=$3
BINARIES_DIR=$4
TARGET_DIR=$5
REGLINUX_BINARIES_DIR=$6

# No U-Boot build step needed — bootloaders are prebuilt Allwinner binary blobs

mkdir -p "${REGLINUX_BINARIES_DIR}/boot/boot"     || exit 1
mkdir -p "${REGLINUX_BINARIES_DIR}/boot/extlinux" || exit 1

cp "${BINARIES_DIR}/Image"              "${REGLINUX_BINARIES_DIR}/boot/boot/linux"              || exit 1
cp "${BINARIES_DIR}/rootfs.cpio.lz4"    "${REGLINUX_BINARIES_DIR}/boot/boot/initrd.lz4"         || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"    "${REGLINUX_BINARIES_DIR}/boot/boot/reglinux.update"    || exit 1
cp "${BINARIES_DIR}/modules"            "${REGLINUX_BINARIES_DIR}/boot/boot/modules.update"     || exit 1
cp "${BINARIES_DIR}/firmware"           "${REGLINUX_BINARIES_DIR}/boot/boot/firmware.update"    || exit 1
cp "${BINARIES_DIR}/rescue"             "${REGLINUX_BINARIES_DIR}/boot/boot/rescue.update"      || exit 1

cp "${BOARD_DIR}/boot/extlinux.conf"    "${REGLINUX_BINARIES_DIR}/boot/extlinux/"               || exit 1
cp "${BOARD_DIR}/bootlogo.bmp"          "${REGLINUX_BINARIES_DIR}/boot/bootlogo.bmp"            || exit 1

# Copy prebuilt Allwinner bootloader blobs needed by genimage
# -L dereferences symlinks so staging area gets real files (fixes broken relative symlinks)
cp -rL "${BOARD_DIR}/partitions"        "${REGLINUX_BINARIES_DIR}/boot/partitions"              || exit 1

# Patch U-Boot env for REG-Linux boot:
# - rdinit=/rdinit → kept (KNULLI trampoline: /rdinit does exec /init, our replaced /init runs)
# - nand_root=LABEL=REGLINUX → setargs_nand puts root=${nand_root} in bootargs;
#   our init reads root= from cmdline — LABEL= doesn't match any case so it falls
#   through to the default MOUNTARG="LABEL=REGLINUX" (correct)
python3 "${BOARD_DIR}/../common/patch-env-img.py" \
    "${REGLINUX_BINARIES_DIR}/boot/partitions/env.img" \
    "nand_root=LABEL=REGLINUX"                                                                  || exit 1

# Inject REG-Linux /init into KNULLI's ramdisk inside boot.img.
# Everything else (kernel, cmdline, busybox, KNULLI /rdinit trampoline) is preserved.
bash "${BOARD_DIR}/../common/patch-boot-img.sh" \
    "${REGLINUX_BINARIES_DIR}/boot/partitions/boot.img" \
    "${BOARD_DIR}/../common/init" \
    "${HOST_DIR}/bin/abootimg"                                                                   || exit 1

exit 0
