#!/bin/bash

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3

# Define U-Boot version we use
UBOOT_VERSION=2023.01

# Define rkbin commit we use
RKBIN_COMMIT=f43a462e7a1429a9d407ae52b4745033034a6cf9

# Define ATF version we use
ATF_VERSION=lts-v2.8.30

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


# Avoid build warnings by editing a .config option in place instead of
# appending an option to .config, if an option is already present
update_config() {
    if ! grep -q "^$1=$2$" .config; then
      if grep -q "^# $1 is not set$" .config; then
        sed -i -e "s/^# $1 is not set$/$1=$2/g" .config
      elif grep -q "^$1=" .config; then
        sed -i -e "s/^$1=.*/$1=$2/g" .config
      else
        echo "$1=$2" >> .config
      fi
    fi
}

# Create target directory
mkdir -p "${IMAGES_DIR}/reglinux/uboot-orangepi-4-lts"

# Build U-Boot
#export BL31=../rkbin/bin/rk33/rk3399_bl31_v1.36.elf
#export ROCKCHIP_TPL=../rkbin/bin/rk33/rk3399_ddr_933MHz_v1.30.bin
export BL31=../arm-trusted-firmware-${ATF_VERSION}/build/rk3399/release/bl31/bl31.elf
export CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-"
ARCH=aarch64 make orangepi_4_lts_rk3399_defconfig
update_config 'CONFIG_IDENT_STRING' '" REG-Linux"'
update_config 'CONFIG_OF_LIBFDT_OVERLAY' 'y'
update_config 'CONFIG_SPL_MMC_SDHCI_SDMA' 'n'
update_config 'CONFIG_MMC_SDHCI_SDMA' 'y'
update_config 'CONFIG_MMC_SPEED_MODE_SET' 'y'
update_config 'CONFIG_MMC_IO_VOLTAGE' 'y'
update_config 'CONFIG_MMC_UHS_SUPPORT' 'y'
update_config 'CONFIG_MMC_HS400_ES_SUPPORT' 'y'
update_config 'CONFIG_MMC_HS400_SUPPORT' 'y'
update_config 'CONFIG_SYS_LOAD_ADDR' '0x800800'
update_config 'CONFIG_TEXT_BASE' '0x00200000'
update_config 'CONFIG_SPL_HAS_BSS_LINKER_SECTION' 'y'
update_config 'CONFIG_SPL_BSS_START_ADDR' '0x400000'
update_config 'CONFIG_SPL_BSS_MAX_SIZE' '0x2000'
update_config 'CONFIG_HAS_CUSTOM_SYS_INIT_SP_ADDR' 'y'
update_config 'CONFIG_CUSTOM_SYS_INIT_SP_ADDR' '0x300000'
ARCH=aarch64 make -j$(nproc)

cp "${IMAGES_DIR}/reglinux/build-uboot-orangepi-4-lts/u-boot-${UBOOT_VERSION}/u-boot-rockchip.bin" "${IMAGES_DIR}/reglinux/uboot-orangepi-4-lts/u-boot-rockchip.bin"

# Rockchip miniloader (idloader.img)
#./tools/mkimage -n rk3399 -T rksd -d ../rkbin/bin/rk33/rk3399_ddr_933MHz_v1.30.bin idbloader.img
#cat ../rkbin/bin/rk33/rk3399_miniloader_v1.30.bin >> idbloader.img
# Copy output
#cp "${IMAGES_DIR}/reglinux/build-uboot-orangepi-4-lts/u-boot-${UBOOT_VERSION}/idbloader.img" "${IMAGES_DIR}/reglinux/uboot-orangepi-4-lts/idbloader.img"

# Rockchip trust.img
#cd ../rkbin
#./tools/trust_merger RKTRUST/RK3399TRUST.ini
# Copy output
#cp "${IMAGES_DIR}/reglinux/build-uboot-orangepi-4-lts/rkbin/trust.img" "${IMAGES_DIR}/reglinux/uboot-orangepi-4-lts/trust.img"

# Pack U-Boot binary with Rockchip loaderimage tool
#cd ../u-boot-${UBOOT_VERSION}
#../rkbin/tools/loaderimage --pack --uboot u-boot-dtb.bin uboot.img 0x200000
# Copy output
#cp "${IMAGES_DIR}/reglinux/build-uboot-orangepi-4-lts/u-boot-${UBOOT_VERSION}/uboot.img" "${IMAGES_DIR}/reglinux/uboot-orangepi-4-lts/uboot.img"
