#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Define U-Boot version we use
UBOOT_VERSION=2025.10

# Download U-Boot mainline
wget "https://ftp.denx.de/pub/u-boot/u-boot-${UBOOT_VERSION}.tar.bz2"

# Extract it
tar xf u-boot-${UBOOT_VERSION}.tar.bz2

# Enter directory
cd u-boot-${UBOOT_VERSION}

# Apply patches if any
PATCHES="${BR2_EXTERNAL_REGLINUX_PATH}/board/allwinner/t527/patches/uboot-orangepi-4a/*.patch"
for patch in $PATCHES
do
echo "Applying patch: $patch"
patch -p1 < $patch
done

# Build bootloader
cp "${BR2_EXTERNAL_REGLINUX_PATH}/board/allwinner/t527/orangepi-4a/bl31.bin" "${BINARIES_DIR}/bl31.bin"
cp "${BR2_EXTERNAL_REGLINUX_PATH}/board/allwinner/t527/orangepi-4a/scp.bin" "${BINARIES_DIR}/scp.bin"
export BL31="${BINARIES_DIR}/bl31.bin"
export SCP="${BINARIES_DIR}/scp.bin"
export CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-"
# NOT IN MAINLINE YET
#ARCH=aarch64 make orangepi-4a_defconfig
ARCH=aarch64 make radxa-cubie-a5e_defconfig
ARCH=aarch64 make -j$(nproc)

# Copy generated files
mkdir -p "${IMAGES_DIR}/reglinux/uboot-orangepi-4a"
cp u-boot-sunxi-with-spl.bin ../../uboot-orangepi-4a/
