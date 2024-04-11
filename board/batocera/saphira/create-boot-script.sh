#!/bin/bash

# HOST_DIR = host dir
# BOARD_DIR = board specific dir
# BUILD_DIR = base dir/build
# BINARIES_DIR = images dir
# TARGET_DIR = target dir
# BATOCERA_BINARIES_DIR = batocera binaries sub directory

HOST_DIR=$1
BOARD_DIR=$2
BUILD_DIR=$3
BINARIES_DIR=$4
TARGET_DIR=$5
BATOCERA_BINARIES_DIR=$6

# No U-Boot, it's on internal drive so far

mkdir -p "${BATOCERA_BINARIES_DIR}/boot/boot"     || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/EFI" || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/EFI/batocera"     || exit 1

cp "${BINARIES_DIR}/Image"           "${BATOCERA_BINARIES_DIR}/boot/boot/linux"           || exit 1
cp "${BINARIES_DIR}/initrd.lz4"      "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.lz4"      || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp "${BINARIES_DIR}/rescue"          "${BATOCERA_BINARIES_DIR}/boot/boot/rescue.update"   || exit 1

# EFI loader
cp -r "${BOARD_DIR}/boot/EFI/BOOT/"           "${BATOCERA_BINARIES_DIR}/boot/EFI/" || exit 1
cp -r "${BOARD_DIR}/boot/EFI/batocera/"           "${BATOCERA_BINARIES_DIR}/boot/EFI/" || exit 1

# Include all dtbs in specific directory
mkdir -p "${BATOCERA_BINARIES_DIR}/boot/dtb/apple"     || exit 1
cp -r "${BINARIES_DIR}/t6000-j314s.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6000-j316s.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6001-j314c.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6001-j316c.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6001-j375c.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6002-j375d.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6020-j414s.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6020-j416s.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6020-j474s.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6021-j414c.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6021-j416c.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6021-j475c.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6022-j180d.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t6022-j475d.dtb"  "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8103-j274.dtb"   "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8103-j293.dtb"   "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8103-j313.dtb"   "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8103-j456.dtb"   "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8103-j457.dtb"   "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8112-j413.dtb"   "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8112-j415.dtb"   "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8112-j473.dtb"   "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1
cp -r "${BINARIES_DIR}/t8112-j493.dtb"   "${BATOCERA_BINARIES_DIR}/boot/dtb/apple/"     || exit 1

exit 0
