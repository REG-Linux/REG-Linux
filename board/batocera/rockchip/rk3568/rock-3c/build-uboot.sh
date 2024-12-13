#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Define U-Boot version we use
UBOOT_VERSION=2025.01-rc4

# Define rkbin commit we use
RKBIN_COMMIT=7c35e21a8529b3758d1f051d1a5dc62aae934b2b

# Download U-Boot
wget "https://ftp.denx.de/pub/u-boot/u-boot-${UBOOT_VERSION}.tar.bz2"

# Extract it
tar xf u-boot-${UBOOT_VERSION}.tar.bz2

# Clone rkbin, checkout our commit
git clone https://github.com/rockchip-linux/rkbin
cd rkbin
git checkout ${RKBIN_COMMIT}
cd ..

# Enter directory
cd u-boot-${UBOOT_VERSION}

# Apply patches if any
PATCHES="${BR2_EXTERNAL_REGLINUX_PATH}/board/batocera/rockchip/rk3568/patches/uboot/*.patch"
for patch in $PATCHES
do
echo "Applying patch: $patch"
patch -p1 < $patch
done

# Build bootloader
export BL31=../rkbin/bin/rk35/rk3568_bl31_v1.44.elf
export ROCKCHIP_TPL=../rkbin/bin/rk35/rk3568_ddr_1056MHz_v1.23.bin
export CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-"
ARCH=aarch64 make rock-3c-rk3566_defconfig
ARCH=aarch64 make -j$(nproc)

# Copy generated files
mkdir -p "${IMAGES_DIR}/reglinux/uboot-rock-3c"
cp "${IMAGES_DIR}/reglinux/build-uboot-rock-3c/u-boot-${UBOOT_VERSION}/u-boot-rockchip.bin" "${IMAGES_DIR}/reglinux/uboot-rock-3c/u-boot-rockchip.bin"

