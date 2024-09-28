#!/bin/bash

# HOST_DIR = host dir
# BOARD_DIR = board specific dir
# BUILD_DIR = base dir/build
# BINARIES_DIR = images dir
# TARGET_DIR = target dir
# REGLINUX_BINARIES_DIR = reglinux binaries sub directory
# BATOCERA_TARGET_DIR = batocera target sub directory

HOST_DIR=$1
BOARD_DIR=$2
BUILD_DIR=$3
BINARIES_DIR=$4
TARGET_DIR=$5
REGLINUX_BINARIES_DIR=$6

mkdir -p "${REGLINUX_BINARIES_DIR}/boot/boot" || exit 1

"${HOST_DIR}/bin/mkimage" -A arm64 -O linux -T kernel -C none -a 0x1080000 -e 0x1080000 -n 5.x -d "${BINARIES_DIR}/Image" "${REGLINUX_BINARIES_DIR}/boot/boot/linux" || exit 1
cp "${BINARIES_DIR}/rootfs.cpio.uboot"  "${REGLINUX_BINARIES_DIR}/boot/boot/uInitrd"            || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"    "${REGLINUX_BINARIES_DIR}/boot/boot/reglinux.update"    || exit 1
cp "${BINARIES_DIR}/modules"            "${REGLINUX_BINARIES_DIR}/boot/boot/modules.update"     || exit 1
cp "${BINARIES_DIR}/firmware"           "${REGLINUX_BINARIES_DIR}/boot/boot/firmware.update"    || exit 1
cp "${BINARIES_DIR}/rescue"             "${REGLINUX_BINARIES_DIR}/boot/boot/rescue.update"      || exit 1

cp "${BINARIES_DIR}/rk3326-odroid-go2.dtb"      "${REGLINUX_BINARIES_DIR}/boot/boot/"   || exit 1
cp "${BINARIES_DIR}/rk3326-odroid-go2-v11.dtb"  "${REGLINUX_BINARIES_DIR}/boot/boot/"   || exit 1
cp "${BINARIES_DIR}/rk3326-odroid-go3.dtb"      "${REGLINUX_BINARIES_DIR}/boot/boot/"   || exit 1
cp "${BINARIES_DIR}/rk3326-gameforce-chi.dtb"   "${REGLINUX_BINARIES_DIR}/boot/boot/"   || exit 1
cp "${BINARIES_DIR}/rk3326-anbernic-rg351m.dtb" "${REGLINUX_BINARIES_DIR}/boot/boot/"   || exit 1
cp "${BINARIES_DIR}/rk3326-anbernic-rg351v.dtb" "${REGLINUX_BINARIES_DIR}/boot/boot/"   || exit 1

cp "${BOARD_DIR}/boot/boot.ini"                 "${REGLINUX_BINARIES_DIR}/boot/"        || exit 1

exit 0
