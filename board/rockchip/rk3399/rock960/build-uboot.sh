#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Define U-Boot version we use
UBOOT_VERSION=2025.01

# Define rkbin commit we use
RKBIN_COMMIT=f43a462e7a1429a9d407ae52b4745033034a6cf9

# Define ATF version we use
ATF_VERSION=lts-v2.12.1

# Download ATF
wget "https://github.com/ARM-software/arm-trusted-firmware/archive/refs/tags/${ATF_VERSION}.tar.gz"
tar xzvf ${ATF_VERSION}.tar.gz
cd arm-trusted-firmware-${ATF_VERSION}
make realclean
make CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-" PLAT=rk3399
cd ..

# Download U-Boot
wget "https://ftp.denx.de/pub/u-boot/u-boot-${UBOOT_VERSION}.tar.bz2"

# Extract it
tar xf u-boot-${UBOOT_VERSION}.tar.bz2

# Clone rkbin, checkout our commit
#git clone https://github.com/rockchip-linux/rkbin
#cd rkbin
#git checkout ${RKBIN_COMMIT}
#cd ..

# Enter directory
cd u-boot-${UBOOT_VERSION}

# Apply patches if any
PATCHES="${BR2_EXTERNAL_REGLINUX_PATH}/board/rockchip/rk3399/patches/uboot-${UBOOT_VERSION}/*.patch"
for patch in $PATCHES
do
echo "Applying patch: $patch"
patch -p1 < $patch
done

# Create target directory
mkdir -p "${IMAGES_DIR}/reglinux/uboot-rock960"

# Build U-Boot
#export BL31=../rkbin/bin/rk33/rk3399_bl31_v1.36.elf
#export ROCKCHIP_TPL=../rkbin/bin/rk33/rk3399_ddr_933MHz_v1.30.bin
export BL31=../arm-trusted-firmware-${ATF_VERSION}/build/rk3399/release/bl31/bl31.elf
export CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-"
ARCH=aarch64 make rock960-rk3399_defconfig
ARCH=aarch64 make -j$(nproc)

cp "${IMAGES_DIR}/reglinux/build-uboot-rock960/u-boot-${UBOOT_VERSION}/u-boot-rockchip.bin" "${IMAGES_DIR}/reglinux/uboot-rock960/u-boot-rockchip.bin"

# Rockchip miniloader (idloader.img)
#./tools/mkimage -n rk3399 -T rksd -d ../rkbin/bin/rk33/rk3399_ddr_933MHz_v1.30.bin idbloader.img
#cat ../rkbin/bin/rk33/rk3399_miniloader_v1.30.bin >> idbloader.img
# Copy output
#cp "${IMAGES_DIR}/reglinux/build-uboot-rock960/u-boot-${UBOOT_VERSION}/idbloader.img" "${IMAGES_DIR}/reglinux/uboot-rock960/idbloader.img"

# Rockchip trust.img
#cd ../rkbin
#./tools/trust_merger RKTRUST/RK3399TRUST.ini
# Copy output
#cp "${IMAGES_DIR}/reglinux/build-uboot-rock960/rkbin/trust.img" "${IMAGES_DIR}/reglinux/uboot-rock960/trust.img"

# Pack U-Boot binary with Rockchip loaderimage tool
#cd ../u-boot-${UBOOT_VERSION}
#../rkbin/tools/loaderimage --pack --uboot u-boot-dtb.bin uboot.img 0x200000
# Copy output
#cp "${IMAGES_DIR}/reglinux/build-uboot-rock960/u-boot-${UBOOT_VERSION}/uboot.img" "${IMAGES_DIR}/reglinux/uboot-rock960/uboot.img"
