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

mkdir -p "${REGLINUX_BINARIES_DIR}/boot/boot"          || exit 1
mkdir -p "${REGLINUX_BINARIES_DIR}/boot/extlinux"      || exit 1
mkdir -p "${REGLINUX_BINARIES_DIR}/boot/dtbs/spacemit" || exit 1

cp "${BINARIES_DIR}/Image.itb"       "${REGLINUX_BINARIES_DIR}/boot/boot/linux"           || exit 1
cp "${BINARIES_DIR}/initrd.lz4"      "${REGLINUX_BINARIES_DIR}/boot/boot/initrd.lz4"      || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${REGLINUX_BINARIES_DIR}/boot/boot/reglinux.update" || exit 1
cp "${BINARIES_DIR}/modules"         "${REGLINUX_BINARIES_DIR}/boot/boot/modules.update"  || exit 1
cp "${BINARIES_DIR}/firmware"        "${REGLINUX_BINARIES_DIR}/boot/boot/firmware.update" || exit 1
cp "${BINARIES_DIR}/rescue"          "${REGLINUX_BINARIES_DIR}/boot/boot/rescue.update"   || exit 1

cp "${BINARIES_DIR}/k1-x_deb1.dtb"    "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
cp "${BINARIES_DIR}/k1-x_deb2.dtb"    "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
cp "${BINARIES_DIR}/k1-x_evb.dtb"     "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
cp "${BINARIES_DIR}/k1-x_MUSE-N1.dtb" "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
cp "${BINARIES_DIR}/k1-x_MUSE-Pi.dtb" "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/splash.bmp"     "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/env_k1-x.txt"   "${REGLINUX_BINARIES_DIR}/boot/" || exit 1
cp "${BOARD_DIR}/boot/extlinux.conf"  "${REGLINUX_BINARIES_DIR}/boot/extlinux/"      || exit 1

exit 0
