#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Clone github master u-boot
git clone https://github.com/u-boot/u-boot

# Clone rkbin
git clone https://github.com/rockchip-linux/rkbin

# Download AArch64 toolchain
wget "https://developer.arm.com/-/media/Files/downloads/gnu/13.3.rel1/binrel/arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-elf.tar.xz?rev=28d5199f6db34e5980aae1062e5a6703&hash=F6F5604BC1A2BBAAEAC4F6E98D8DC35B" -O arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-elf.tar.xz
tar -xf arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-elf.tar.xz
export PATH=$(pwd)/arm-gnu-toolchain-13.3.rel1-x86_64-aarch64-none-elf/bin:$PATH

# Enter directory
cd u-boot

# Apply patches if any
PATCHES="${BR2_EXTERNAL_REGLINUX_PATH}/board/batocera/rockchip/rk3568/patches/uboot/*.patch"
for patch in $PATCHES
do
echo "Applying patch: $patch"
patch -p1 < $patch
done

# Build it
export CROSS_COMPILE=aarch64-none-elf-
export BL31=../rkbin/bin/rk35/rk3568_bl31_v1.44.elf
export ROCKCHIP_TPL=../rkbin/bin/rk35/rk3568_ddr_1056MHz_v1.23.bin
export CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-"
ARCH=aarch64 make anbernic-rgxx3-rk3566_defconfig
ARCH=aarch64 make -j$(nproc)

# Copy generated files
mkdir -p "${IMAGES_DIR}/reglinux/uboot-anbernic-rgxx3"
cp "${IMAGES_DIR}/reglinux/build-uboot-anbernic-rgxx3/u-boot/u-boot-rockchip.bin" "${IMAGES_DIR}/reglinux/uboot-anbernic-rgxx3/u-boot-rockchip.bin"
#cp "${IMAGES_DIR}/reglinux/build-uboot-anbernic-rgxx3/u-boot/u-boot.bin"          "${IMAGES_DIR}/reglinux/uboot-anbernic-rgxx3/u-boot.bin"
