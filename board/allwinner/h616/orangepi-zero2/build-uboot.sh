#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Define U-Boot version we use
UBOOT_VERSION=2025.01

# Download U-Boot mainline
wget "https://ftp.denx.de/pub/u-boot/u-boot-${UBOOT_VERSION}.tar.bz2"

# Extract it
tar xf u-boot-${UBOOT_VERSION}.tar.bz2

# Enter directory
cd u-boot-${UBOOT_VERSION}

# Apply patches if any
PATCHES="${BR2_EXTERNAL_REGLINUX_PATH}/board/allwinner/h616/patches/u-boot/*.patch"
for patch in $PATCHES
do
echo "Applying patch: $patch"
patch -p1 < $patch
done

# Build bootloader
export BL31="${BINARIES_DIR}/bl31.bin"
export CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-musl-"
ARCH=aarch64 make orangepi_zero2_defconfig
ARCH=aarch64 make -j$(nproc)

# Copy generated files
mkdir -p "${IMAGES_DIR}/reglinux/uboot-orangepi-zero2"
cp u-boot-sunxi-with-spl.bin ../../uboot-orangepi-zero2/
