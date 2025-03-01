#!/bin/bash -e

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
REGLINUX_TARGET_DIR=$7

# /boot
rm -rf "${REGLINUX_BINARIES_DIR}/boot"     || exit 1
mkdir -p "${REGLINUX_BINARIES_DIR}/boot"     || exit 1
mkdir "${REGLINUX_BINARIES_DIR}/boot/boot"     || exit 1
mkdir "${REGLINUX_BINARIES_DIR}/boot/proc"     || exit 1
mkdir "${REGLINUX_BINARIES_DIR}/boot/dev"     || exit 1
mkdir "${REGLINUX_BINARIES_DIR}/boot/root"     || exit 1

# boot.tar.xz
cp "${BINARIES_DIR}/rootfs.cpio.lz4"      "${REGLINUX_BINARIES_DIR}/boot/boot/initrd.lz4" || exit 1
#cp "${BOARD_DIR}/boot/extlinux.conf"     "${REGLINUX_BINARIES_DIR}/boot/extlinux/"       || exit 1

cp "${BINARIES_DIR}/rootfs.squashfs" "${REGLINUX_BINARIES_DIR}/boot/boot/reglinux.update" || exit 1
cp "${BINARIES_DIR}/uzImage.bin"     "${REGLINUX_BINARIES_DIR}/uzImage.bin.source"        || exit 1
cp "${BINARIES_DIR}/mininit-syspart" "${REGLINUX_BINARIES_DIR}/boot/mininit-syspart"      || exit 1
cp "${BINARIES_DIR}/ubiboot-v11_ddr2_512mb.bin" "${REGLINUX_BINARIES_DIR}/boot/ubiboot.bin" || exit 1
cp "${BINARIES_DIR}/gcw0_proto.dtb" "${REGLINUX_BINARIES_DIR}/boot/gcw0_proto.dtb" || exit 1
cp "${BINARIES_DIR}/gcw0.dtb" "${REGLINUX_BINARIES_DIR}/boot/gcw0.dtb" || exit 1
cp "${BINARIES_DIR}/rg350.dtb" "${REGLINUX_BINARIES_DIR}/boot/rg350.dtb" || exit 1
cp "${BINARIES_DIR}/rg350m.dtb" "${REGLINUX_BINARIES_DIR}/boot/rg350m.dtb" || exit 1
cp "${BINARIES_DIR}/rg280m-v1.0.dtb" "${REGLINUX_BINARIES_DIR}/boot/rg280m-v1.0.dtb" || exit 1
cp "${BINARIES_DIR}/rg280m-v1.1.dtb" "${REGLINUX_BINARIES_DIR}/boot/rg280m-v1.1.dtb" || exit 1
cp "${BINARIES_DIR}/rg280v.dtb" "${REGLINUX_BINARIES_DIR}/boot/rg280v.dtb" || exit 1

# model select(rg350,rg350m,rg280m,rg280v,gcw0(no test))
cat "${REGLINUX_BINARIES_DIR}/uzImage.bin.source" "${REGLINUX_BINARIES_DIR}/boot/rg280v.dtb" > "${REGLINUX_BINARIES_DIR}/boot/uzImage.bin" || exit 1
