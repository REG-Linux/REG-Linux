#!/bin/bash
set -euo pipefail

usage() {
    cat <<EOF
Usage: $0 HOST_DIR BOARD_DIR BINARIES_DIR IMAGES_DIR UBOOT_DEFCONFIG UBOOT_TARGET

Builds U-Boot 2025.01 for an Allwinner H616 board by reusing cached sources and
declaring the BL31/TPL blobs from the Buildroot binaries directory.
EOF
}

if [ "$#" -ne 6 ]; then
    usage
    exit 1
fi

HOST_DIR=$1
BOARD_DIR=$2
BINARIES_DIR=$3
IMAGES_DIR=$4
UBOOT_DEFCONFIG=$5
UBOOT_TARGET=$6

: "${BR2_EXTERNAL_REGLINUX_PATH:?BR2_EXTERNAL_REGLINUX_PATH must be set}"

readonly UBOOT_VERSION=2025.01

RESULT_BASE="${IMAGES_DIR}"
CACHE_DIR="${RESULT_BASE}/build-uboot-cache"
TARBALL="${CACHE_DIR}/u-boot-${UBOOT_VERSION}.tar.bz2"
SOURCE_CACHE="${CACHE_DIR}/u-boot-${UBOOT_VERSION}"

mkdir -p "${CACHE_DIR}"

if [ ! -f "${TARBALL}" ]; then
    echo "Downloading U-Boot ${UBOOT_VERSION}"
    wget -O "${TARBALL}" "https://ftp.denx.de/pub/u-boot/u-boot-${UBOOT_VERSION}.tar.bz2"
fi

if [ ! -d "${SOURCE_CACHE}" ]; then
    tar -xjf "${TARBALL}" -C "${CACHE_DIR}"
fi

WORK_DIR="$(pwd)"

rm -rf "${WORK_DIR}/u-boot-${UBOOT_VERSION}"
cp -a "${SOURCE_CACHE}" "${WORK_DIR}"

UBOOT_SRC="${WORK_DIR}/u-boot-${UBOOT_VERSION}"

pushd "${UBOOT_SRC}" >/dev/null

PATCH_DIR="${BR2_EXTERNAL_REGLINUX_PATH}/board/allwinner/h616/patches/u-boot"
for patch in "${PATCH_DIR}"/*.patch; do
    [ -e "${patch}" ] || continue
    echo "Applying patch: ${patch}"
    patch -p1 < "${patch}"
done

export BL31="${BINARIES_DIR}/bl31.bin"
export CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-musl-"
ARCH=aarch64 make "${UBOOT_DEFCONFIG}"
ARCH=aarch64 make -j"$(nproc)"

popd >/dev/null

mkdir -p "${RESULT_BASE}/uboot-${UBOOT_TARGET}"
cp "${UBOOT_SRC}/u-boot-sunxi-with-spl.bin" "${RESULT_BASE}/uboot-${UBOOT_TARGET}/u-boot-sunxi-with-spl.bin"
