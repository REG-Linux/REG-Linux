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

BUILD_SCRIPT="$(dirname "${BOARD_DIR}")/build-uboot.sh"
BUILD_DIR="${REGLINUX_BINARIES_DIR}/build-uboot-anbernic-rgxx3"
mkdir -p "${BUILD_DIR}" || exit 1
cp "${BUILD_SCRIPT}" "${BUILD_DIR}/" || exit 1
cd "${BUILD_DIR}" && ./build-uboot.sh "${HOST_DIR}" "${BOARD_DIR}" "${REGLINUX_BINARIES_DIR}" "anbernic-rgxx3-rk3566_defconfig" "anbernic-rgxx3" || exit 1

mkdir -p "${REGLINUX_BINARIES_DIR}/boot/boot/extlinux" || exit 1

cp "${BINARIES_DIR}/Image"              "${REGLINUX_BINARIES_DIR}/boot/boot/linux"              || exit 1
cp "${BINARIES_DIR}/rootfs.cpio.lz4"    "${REGLINUX_BINARIES_DIR}/boot/boot/initrd.lz4"         || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"    "${REGLINUX_BINARIES_DIR}/boot/boot/reglinux.update"    || exit 1
cp "${BINARIES_DIR}/modules"            "${REGLINUX_BINARIES_DIR}/boot/boot/modules.update"     || exit 1
cp "${BINARIES_DIR}/firmware"           "${REGLINUX_BINARIES_DIR}/boot/boot/firmware.update"    || exit 1
cp "${BINARIES_DIR}/rescue"             "${REGLINUX_BINARIES_DIR}/boot/boot/rescue.update"      || exit 1

cp "${BINARIES_DIR}/rk3566-anbernic-rg353p.dtb"     "${REGLINUX_BINARIES_DIR}/boot/boot/rk3566-anbernic-rg353p.dtb"  || exit 1
cp "${BINARIES_DIR}/rk3566-anbernic-rg353ps.dtb"    "${REGLINUX_BINARIES_DIR}/boot/boot/rk3566-anbernic-rg353ps.dtb" || exit 1
cp "${BINARIES_DIR}/rk3566-anbernic-rg353v.dtb"     "${REGLINUX_BINARIES_DIR}/boot/boot/rk3566-anbernic-rg353v.dtb"  || exit 1
cp "${BINARIES_DIR}/rk3566-anbernic-rg353vs.dtb"    "${REGLINUX_BINARIES_DIR}/boot/boot/rk3566-anbernic-rg353vs.dtb" || exit 1
cp "${BINARIES_DIR}/rk3566-anbernic-rg503.dtb"      "${REGLINUX_BINARIES_DIR}/boot/boot/rk3566-anbernic-rg503.dtb"   || exit 1

cp "${BINARIES_DIR}/rk3566-powkiddy-rgb10max3.dtb"  "${REGLINUX_BINARIES_DIR}/boot/boot/rk3566-powkiddy-rgb10max3.dtb" || exit 1
cp "${BINARIES_DIR}/rk3566-powkiddy-rgb30.dtb"      "${REGLINUX_BINARIES_DIR}/boot/boot/rk3566-powkiddy-rgb30.dtb"     || exit 1
cp "${BINARIES_DIR}/rk3566-powkiddy-rk2023.dtb"     "${REGLINUX_BINARIES_DIR}/boot/boot/rk3566-powkiddy-rk2023.dtb"    || exit 1
# Powkiddy X55 needs a specific U-Boot hence target / image, so we do NOT include it here

cp "${BOARD_DIR}/boot/extlinux.conf"        "${REGLINUX_BINARIES_DIR}/boot/boot/extlinux/" || exit 1

# Android based bootloader workaround
UBOOT_DIR="$(dirname "${REGLINUX_BINARIES_DIR}")/uboot-anbernic-rgxx3"
cp "${UBOOT_DIR}/u-boot-rockchip.bin" "${REGLINUX_BINARIES_DIR}/boot/boot/u-boot-rockchip.bin" || exit 1
[ -f "${UBOOT_DIR}/u-boot.itb" ] && cp "${UBOOT_DIR}/u-boot.itb" "${REGLINUX_BINARIES_DIR}/boot/boot/u-boot.itb"
cp "${BOARD_DIR}/boot/boot.cmd"                               "${REGLINUX_BINARIES_DIR}/boot/boot.cmd"   || exit 1
cp "${BOARD_DIR}/boot/boot.scr"                               "${REGLINUX_BINARIES_DIR}/boot/boot.scr"   || exit 1

exit 0
