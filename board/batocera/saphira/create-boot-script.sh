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

# No U-Boot, it's on internal drive so far

mkdir -p "${REGLINUX_BINARIES_DIR}/boot/boot"     || exit 1
mkdir -p "${REGLINUX_BINARIES_DIR}/boot/EFI" || exit 1
mkdir -p "${REGLINUX_BINARIES_DIR}/boot/EFI/batocera"     || exit 1

cp "${BINARIES_DIR}/Image"              "${REGLINUX_BINARIES_DIR}/boot/boot/linux"           || exit 1
cp "${BINARIES_DIR}/rootfs.cpio.lz4"    "${REGLINUX_BINARIES_DIR}/boot/boot/initrd.lz4"      || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"    "${REGLINUX_BINARIES_DIR}/boot/boot/reglinux.update" || exit 1
cp "${BINARIES_DIR}/rescue"             "${REGLINUX_BINARIES_DIR}/boot/boot/rescue.update"   || exit 1

# EFI loader
cp -r "${BOARD_DIR}/boot/EFI/BOOT/"     "${REGLINUX_BINARIES_DIR}/boot/EFI/" || exit 1
cp -r "${BOARD_DIR}/boot/EFI/batocera/" "${REGLINUX_BINARIES_DIR}/boot/EFI/" || exit 1

# Include all dtbs in specific directory
mkdir -p "${REGLINUX_BINARIES_DIR}/boot/dtb/apple"     || exit 1
cp -r "${BINARIES_DIR}/t6000-j314s.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6000-j316s.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6001-j314c.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6001-j316c.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6001-j375c.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6002-j375d.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6020-j414s.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6020-j416s.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6020-j474s.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6021-j414c.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6021-j416c.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6021-j475c.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6022-j180d.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6022-j475d.dtb"  "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8103-j274.dtb"   "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8103-j293.dtb"   "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8103-j313.dtb"   "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8103-j456.dtb"   "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8103-j457.dtb"   "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8112-j413.dtb"   "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8112-j415.dtb"   "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8112-j473.dtb"   "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8112-j493.dtb"   "${REGLINUX_BINARIES_DIR}/boot/dtb/apple/"     || exit 1

exit 0
