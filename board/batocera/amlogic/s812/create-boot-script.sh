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

cp "${BINARIES_DIR}/uImage"             "${REGLINUX_BINARIES_DIR}/boot/boot/uImage"          || exit 1
cp "${BINARIES_DIR}/rootfs.cpio.uboot"  "${REGLINUX_BINARIES_DIR}/boot/boot/uInitrd"         || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"    "${REGLINUX_BINARIES_DIR}/boot/boot/reglinux.update" || exit 1
cp "${BINARIES_DIR}/modules"            "${REGLINUX_BINARIES_DIR}/boot/boot/modules.update"  || exit 1
cp "${BINARIES_DIR}/firmware"           "${REGLINUX_BINARIES_DIR}/boot/boot/firmware.update" || exit 1
cp "${BINARIES_DIR}/rescue"             "${REGLINUX_BINARIES_DIR}/boot/boot/rescue.update"   || exit 1

cp "${BINARIES_DIR}/meson8m2-mxiii.dtb"         "${REGLINUX_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BINARIES_DIR}/meson8m2-mxiii-plus.dtb"    "${REGLINUX_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BINARIES_DIR}/meson8m2-m8s.dtb"           "${REGLINUX_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BINARIES_DIR}/meson8-minix-neo-x8.dtb"    "${REGLINUX_BINARIES_DIR}/boot/boot/"     || exit 1
cp "${BINARIES_DIR}/meson8-tronsmart-s82.dtb"   "${REGLINUX_BINARIES_DIR}/boot/boot/"     || exit 1
# cp "${BINARIES_DIR}/meson8m2-wetek-core.dtb" "${REGLINUX_BINARIES_DIR}/boot/boot/"     || exit 1

"${HOST_DIR}/bin/mkimage" -C none -A arm -T script -d "${BOARD_DIR}/boot/s805_autoscript.cmd" "${REGLINUX_BINARIES_DIR}/boot/s805_autoscript" || exit 1
"${HOST_DIR}/bin/mkimage" -C none -A arm -T script -d "${BOARD_DIR}/boot/aml_autoscript.scr"  "${REGLINUX_BINARIES_DIR}/boot/aml_autoscript"  || exit 1
cp "${BOARD_DIR}/boot/uEnv.txt" "${REGLINUX_BINARIES_DIR}/boot/uEnv.txt" || exit 1
cp "${BOARD_DIR}/boot/aml_autoscript.zip" "${REGLINUX_BINARIES_DIR}/boot/" || exit 1

cp "${BOARD_DIR}/boot/boot-custom.sh"     "${REGLINUX_BINARIES_DIR}/boot/" || exit 1

exit 0
