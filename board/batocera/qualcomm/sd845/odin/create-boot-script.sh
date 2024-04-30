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

cp "${BINARIES_DIR}/Image"           "${REGLINUX_BINARIES_DIR}/boot/boot/Image"           || exit 1
cp "${BINARIES_DIR}/initrd.lz4"      "${REGLINUX_BINARIES_DIR}/boot/boot/initrd.lz4"      || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs" "${REGLINUX_BINARIES_DIR}/boot/boot/reglinux.update" || exit 1
cp "${BINARIES_DIR}/modules"         "${REGLINUX_BINARIES_DIR}/boot/boot/modules.update"  || exit 1
cp "${BINARIES_DIR}/firmware"        "${REGLINUX_BINARIES_DIR}/boot/boot/firmware.update" || exit 1
cp "${BINARIES_DIR}/rescue"          "${REGLINUX_BINARIES_DIR}/boot/boot/rescue.update"   || exit 1

cp "${BINARIES_DIR}/sdm845-ayn-odin.dtb"    "${REGLINUX_BINARIES_DIR}/boot/boot/"           || exit 1
cp -f "${BOARD_DIR}/grub.cfg"               "${BINARIES_DIR}/efi-part/EFI/BOOT/grub.cfg"    || exit 1
cp -r "${BINARIES_DIR}/efi-part/EFI/"       "${REGLINUX_BINARIES_DIR}/boot/"                || exit 1

exit 0
