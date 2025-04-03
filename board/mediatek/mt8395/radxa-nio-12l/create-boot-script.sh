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

mkdir -p "${REGLINUX_BINARIES_DIR}/boot/boot"         || exit 1
mkdir -p "${REGLINUX_BINARIES_DIR}/boot/boot/efi"     || exit 1
mkdir -p "${REGLINUX_BINARIES_DIR}/boot/boot/grub"    || exit 1
mkdir -p "${REGLINUX_BINARIES_DIR}/EFI/BOOT"          || exit 1
mkdir -p "${REGLINUX_BINARIES_DIR}/boot/EFI/BOOT"     || exit 1
mkdir -p "${REGLINUX_BINARIES_DIR}/boot/extlinux"     || exit 1

cp "${BINARIES_DIR}/Image"              "${REGLINUX_BINARIES_DIR}/boot/boot/linux"           || exit 1
cp "${BINARIES_DIR}/rootfs.cpio.lz4"    "${REGLINUX_BINARIES_DIR}/boot/boot/initrd.lz4"      || exit 1
cp "${BINARIES_DIR}/rootfs.squashfs"    "${REGLINUX_BINARIES_DIR}/boot/boot/reglinux.update" || exit 1
cp "${BINARIES_DIR}/modules"            "${REGLINUX_BINARIES_DIR}/boot/boot/modules.update"  || exit 1
cp "${BINARIES_DIR}/firmware"           "${REGLINUX_BINARIES_DIR}/boot/boot/firmware.update" || exit 1
cp "${BINARIES_DIR}/rescue"             "${REGLINUX_BINARIES_DIR}/boot/boot/rescue.update"   || exit 1

cp "${BINARIES_DIR}/mt8395-radxa-nio-12l.dtb"        "${REGLINUX_BINARIES_DIR}/boot/boot/"                 || exit 1
cp "${BOARD_DIR}/boot/grub/grub.cfg"                 "${REGLINUX_BINARIES_DIR}/boot/EFI/BOOT/grub.cfg"     || exit 1
cp "${BINARIES_DIR}/efi-part/EFI/BOOT/bootaa64.efi"  "${REGLINUX_BINARIES_DIR}/boot/EFI/BOOT/BOOTAA64.EFI" || exit 1

exit 0
