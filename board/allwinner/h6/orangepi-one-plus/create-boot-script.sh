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

UBOOT_SCRIPT="$(dirname "${BOARD_DIR}")/build-uboot.sh"
UBOOT_DEFCONFIG="orangepi_one_plus_defconfig"
UBOOT_TARGET="orangepi-one-plus"

mkdir -p "${REGLINUX_BINARIES_DIR}/build-uboot-${UBOOT_TARGET}"     || exit 1
cd "${REGLINUX_BINARIES_DIR}/build-uboot-${UBOOT_TARGET}" && "${UBOOT_SCRIPT}" \
    "${HOST_DIR}" "${BOARD_DIR}" "${BINARIES_DIR}" "${REGLINUX_BINARIES_DIR}" "${UBOOT_DEFCONFIG}" "${UBOOT_TARGET}" || exit 1

mkdir -p "${REGLINUX_BINARIES_DIR}/boot/boot"     || exit 1
mkdir -p "${REGLINUX_BINARIES_DIR}/boot/extlinux" || exit 1

cp "${BINARIES_DIR}/Image"              "${REGLINUX_BINARIES_DIR}/boot/boot/linux"           || exit 1
cp "${BINARIES_DIR}/rootfs.cpio.lz4"    "${REGLINUX_BINARIES_DIR}/boot/boot/initrd.lz4"      || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"    "${REGLINUX_BINARIES_DIR}/boot/boot/reglinux.update" || exit 1
cp "${BINARIES_DIR}/modules"            "${REGLINUX_BINARIES_DIR}/boot/boot/modules.update"  || exit 1
cp "${BINARIES_DIR}/firmware"           "${REGLINUX_BINARIES_DIR}/boot/boot/firmware.update" || exit 1
cp "${BINARIES_DIR}/rescue"             "${REGLINUX_BINARIES_DIR}/boot/boot/rescue.update"   || exit 1

cp "${BINARIES_DIR}/sun50i-h6-orangepi-one-plus.dtb"    "${REGLINUX_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BOARD_DIR}/boot/extlinux.conf"                    "${REGLINUX_BINARIES_DIR}/boot/extlinux/" || exit 1

exit 0
