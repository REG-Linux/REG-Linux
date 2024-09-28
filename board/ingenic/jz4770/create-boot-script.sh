#!/bin/bash -e

# HOST_DIR = host dir
# BOARD_DIR = board specific dir
# BUILD_DIR = base dir/build
# BINARIES_DIR = images dir
# TARGET_DIR = target dir
# BATOCERA_BINARIES_DIR = batocera binaries sub directory
# BATOCERA_TARGET_DIR = batocera target sub directory

HOST_DIR=$1
BOARD_DIR=$2
BUILD_DIR=$3
BINARIES_DIR=$4
TARGET_DIR=$5
BATOCERA_BINARIES_DIR=$6
BATOCERA_TARGET_DIR=$7

# /boot
rm -rf "${BATOCERA_BINARIES_DIR}/boot"     || exit 1
mkdir -p "${BATOCERA_BINARIES_DIR}/boot"     || exit 1
mkdir "${BATOCERA_BINARIES_DIR}/boot/boot"     || exit 1
mkdir "${BATOCERA_BINARIES_DIR}/boot/proc"     || exit 1
mkdir "${BATOCERA_BINARIES_DIR}/boot/dev"     || exit 1
mkdir "${BATOCERA_BINARIES_DIR}/boot/root"     || exit 1

# boot.tar.xz
cp "${BINARIES_DIR}/rootfs.cpio.lz4"      "${BATOCERA_BINARIES_DIR}/boot/boot/initrd.lz4" || exit 1
#cp "${BOARD_DIR}/boot/extlinux.conf"     "${BATOCERA_BINARIES_DIR}/boot/extlinux/"       || exit 1

cp "${BINARIES_DIR}/rootfs.squashfs" "${BATOCERA_BINARIES_DIR}/boot/boot/batocera.update" || exit 1
cp "${BINARIES_DIR}/uzImage.bin"     "${BATOCERA_BINARIES_DIR}/uzImage.bin.source"        || exit 1
cp "${BINARIES_DIR}/mininit-syspart" "${BATOCERA_BINARIES_DIR}/boot/mininit-syspart"      || exit 1
cp "${BINARIES_DIR}/ubiboot-v11_ddr2_512mb.bin" "${BATOCERA_BINARIES_DIR}/boot/ubiboot.bin" || exit 1
cp "${BINARIES_DIR}/gcw0_proto.dtb" "${BATOCERA_BINARIES_DIR}/boot/gcw0_proto.dtb" || exit 1
cp "${BINARIES_DIR}/gcw0.dtb" "${BATOCERA_BINARIES_DIR}/boot/gcw0.dtb" || exit 1
cp "${BINARIES_DIR}/rg350.dtb" "${BATOCERA_BINARIES_DIR}/boot/rg350.dtb" || exit 1
cp "${BINARIES_DIR}/rg350m.dtb" "${BATOCERA_BINARIES_DIR}/boot/rg350m.dtb" || exit 1
cp "${BINARIES_DIR}/rg280m-v1.0.dtb" "${BATOCERA_BINARIES_DIR}/boot/rg280m-v1.0.dtb" || exit 1
cp "${BINARIES_DIR}/rg280m-v1.1.dtb" "${BATOCERA_BINARIES_DIR}/boot/rg280m-v1.1.dtb" || exit 1
cp "${BINARIES_DIR}/rg280v.dtb" "${BATOCERA_BINARIES_DIR}/boot/rg280v.dtb" || exit 1

# model select(rg350,rg350m,rg280m,rg280v,gcw0(no test))
cat "${BATOCERA_BINARIES_DIR}/uzImage.bin.source" "${BATOCERA_BINARIES_DIR}/boot/rg280v.dtb" > "${BATOCERA_BINARIES_DIR}/boot/uzImage.bin" || exit 1
