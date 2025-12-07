#!/bin/bash
set -euo pipefail

usage() {
    cat <<EOF
Usage: $0 HOST_DIR BOARD_DIR IMAGES_DIR UBOOT_DEFCONFIG UBOOT_TARGET

This script reuses cached U-Boot and rkbin sources to build Rockchip RK3588 bootloaders.
EOF
}

if [ "$#" -ne 5 ]; then
    usage
    exit 1
fi

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3
UBOOT_DEFCONFIG=$4
UBOOT_TARGET=$5

: "${BR2_EXTERNAL_REGLINUX_PATH:?BR2_EXTERNAL_REGLINUX_PATH must be set}"

readonly UBOOT_VERSION=2025.10
readonly RKBIN_COMMIT=7c35e21a8529b3758d1f051d1a5dc62aae934b2b

RESULT_BASE="${IMAGES_DIR}/reglinux"
CACHE_DIR="${RESULT_BASE}/build-uboot-cache"
TARBALL="${CACHE_DIR}/u-boot-${UBOOT_VERSION}.tar.bz2"
SOURCE_CACHE="${CACHE_DIR}/u-boot-${UBOOT_VERSION}"
RKBIN_CACHE="${CACHE_DIR}/rkbin"

mkdir -p "${CACHE_DIR}"

if [ ! -f "${TARBALL}" ]; then
    echo "Downloading U-Boot ${UBOOT_VERSION}"
    wget -O "${TARBALL}" "https://ftp.denx.de/pub/u-boot/u-boot-${UBOOT_VERSION}.tar.bz2"
fi

if [ ! -d "${SOURCE_CACHE}" ]; then
    tar -xjf "${TARBALL}" -C "${CACHE_DIR}"
fi

if [ ! -d "${RKBIN_CACHE}" ]; then
    git clone https://github.com/rockchip-linux/rkbin "${RKBIN_CACHE}"
fi

if ! git -C "${RKBIN_CACHE}" rev-parse --verify --quiet "${RKBIN_COMMIT}^{commit}" >/dev/null 2>&1; then
    git -C "${RKBIN_CACHE}" fetch --depth=1 origin "${RKBIN_COMMIT}"
fi

git -C "${RKBIN_CACHE}" checkout --force "${RKBIN_COMMIT}"
git -C "${RKBIN_CACHE}" reset --hard "${RKBIN_COMMIT}"

WORK_DIR="$(pwd)"

rm -rf "${WORK_DIR}/u-boot-${UBOOT_VERSION}"
cp -a "${SOURCE_CACHE}" "${WORK_DIR}"

UBOOT_SRC="${WORK_DIR}/u-boot-${UBOOT_VERSION}"

RK35_BIN="${RKBIN_CACHE}/bin/rk35"

pushd "${UBOOT_SRC}" >/dev/null

PATCH_DIR="${BR2_EXTERNAL_REGLINUX_PATH}/board/rockchip/rk3588/patches/uboot"
for patch in "${PATCH_DIR}"/*.patch; do
    [ -e "${patch}" ] || continue
    echo "Applying patch: ${patch}"
    patch -p1 < "${patch}"
done

export BL31="${RK35_BIN}/rk3588_bl31_v1.47.elf"
export ROCKCHIP_TPL="${RK35_BIN}/rk3588_ddr_lp4_2112MHz_lp5_2400MHz_v1.18.bin"
export CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-"
ARCH=aarch64 make "${UBOOT_DEFCONFIG}"
ARCH=aarch64 make -j"$(nproc)"

popd >/dev/null

mkdir -p "${RESULT_BASE}/uboot-${UBOOT_TARGET}"
cp "${UBOOT_SRC}/u-boot-rockchip.bin" "${RESULT_BASE}/uboot-${UBOOT_TARGET}/u-boot-rockchip.bin"
