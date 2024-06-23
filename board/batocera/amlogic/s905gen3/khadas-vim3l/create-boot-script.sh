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

mkdir -p "${REGLINUX_BINARIES_DIR}/build-uboot-vim3l"     || exit 1
cp "${BOARD_DIR}/build-uboot.sh"          "${REGLINUX_BINARIES_DIR}/build-uboot-vim3l/" || exit 1
cd "${REGLINUX_BINARIES_DIR}/build-uboot-vim3l/" && ./build-uboot.sh "${HOST_DIR}" "${BOARD_DIR}" "${BINARIES_DIR}" || exit 1

mkdir -p "${REGLINUX_BINARIES_DIR}/boot/boot"     || exit 1
mkdir -p "${REGLINUX_BINARIES_DIR}/boot/extlinux" || exit 1

cp "${BINARIES_DIR}/Image"              "${REGLINUX_BINARIES_DIR}/boot/boot/linux"              || exit 1
cp "${BINARIES_DIR}/rootfs.cpio.lz4"    "${REGLINUX_BINARIES_DIR}/boot/boot/initrd.lz4"         || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"    "${REGLINUX_BINARIES_DIR}/boot/boot/reglinux.update"    || exit 1
cp "${BINARIES_DIR}/modules"            "${REGLINUX_BINARIES_DIR}/boot/boot/modules.update"     || exit 1
cp "${BINARIES_DIR}/firmware"           "${REGLINUX_BINARIES_DIR}/boot/boot/firmware.update"    || exit 1
cp "${BINARIES_DIR}/meson-sm1-khadas-vim3l.dtb" "${REGLINUX_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BOARD_DIR}/boot/extlinux.conf"            "${REGLINUX_BINARIES_DIR}/boot/extlinux/" || exit 1

# Handle Khadas vendor u-boot installed on eMMC
# We chainload to mainline U-Boot through vendor scripts
# First, copy the scripts (source+compiled)
cp "${BOARD_DIR}/boot/boot.ini"                 "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/boot.scr"                 "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/aml_autoscript"           "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/aml_autoscript.txt"       "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/aml_autoscript.zip"       "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/s905_autoscript.cmd"      "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/s905_autoscript"          "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
# Finally, copy the u-boot.bin raw payload (mainline) to root of SD card as u-boot.bin
cp "${REGLINUX_BINARIES_DIR}/uboot-vim3l/u-boot.raw" "${REGLINUX_BINARIES_DIR}/boot/u-boot.bin" || exit 1

exit 0
