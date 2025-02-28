#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Define U-Boot version we use
UBOOT_VERSION=2025.01

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
PATCHES="${BR2_EXTERNAL_REGLINUX_PATH}/board/rockchip/rk3588/patches/uboot/*.patch"
for patch in $PATCHES
do
echo "Applying patch: $patch"
patch -p1 < $patch
done

# Build bootloader
export BL31=../rkbin/bin/rk35/rk3588_bl31_v1.47.elf
export ROCKCHIP_TPL=../rkbin/bin/rk35/rk3588_ddr_lp4_2112MHz_lp5_2400MHz_v1.18.bin
export CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-"
ARCH=aarch64 make orangepi-5-plus-rk3588_defconfig
ARCH=aarch64 make -j$(nproc)

# Copy generated files
mkdir -p "${IMAGES_DIR}/reglinux/uboot-orangepi-5-plus"
cp "${IMAGES_DIR}/reglinux/build-uboot-orangepi-5-plus/u-boot-${UBOOT_VERSION}/u-boot-rockchip.bin" "${IMAGES_DIR}/reglinux/uboot-orangepi-5-plus/u-boot-rockchip.bin"

