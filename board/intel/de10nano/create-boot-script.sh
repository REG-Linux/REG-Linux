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

mkdir -p "${REGLINUX_BINARIES_DIR}/boot/boot"     || exit 1

cp "${BINARIES_DIR}/zImage"             "${REGLINUX_BINARIES_DIR}/boot/boot/zImage"          || exit 1
cp "${BINARIES_DIR}/rootfs.cpio.lz4"    "${REGLINUX_BINARIES_DIR}/boot/boot/initrd.lz4"     || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"    "${REGLINUX_BINARIES_DIR}/boot/boot/reglinux.update" || exit 1
cp "${BINARIES_DIR}/modules"            "${REGLINUX_BINARIES_DIR}/boot/boot/modules.update"  || exit 1
cp "${BINARIES_DIR}/firmware"           "${REGLINUX_BINARIES_DIR}/boot/boot/firmware.update"  || exit 1
cp "${BINARIES_DIR}/rescue"             "${REGLINUX_BINARIES_DIR}/boot/boot/rescue.update"   || exit 1

# Device tree
cp "${BINARIES_DIR}/socfpga_cyclone5_de10_nano.dtb" "${REGLINUX_BINARIES_DIR}/boot/boot/" || exit 1

# U-Boot boot script
"${HOST_DIR}/bin/mkimage" -C none -A arm -T script -d "${BOARD_DIR}/boot/boot.cmd" "${REGLINUX_BINARIES_DIR}/boot/boot.scr" || exit 1

# Copy extlinux config as fallback
cp "${BOARD_DIR}/boot/boot.ini" "${REGLINUX_BINARIES_DIR}/boot/boot.ini" || exit 1

# U-Boot SPL+U-Boot image for raw 0xA2 partition
cp "${BINARIES_DIR}/u-boot-with-spl.sfp" "${REGLINUX_BINARIES_DIR}/boot/u-boot-with-spl.sfp" || exit 1

exit 0
