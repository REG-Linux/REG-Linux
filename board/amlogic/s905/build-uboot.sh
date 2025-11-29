#!/bin/bash
set -euo pipefail

trap 'rc=$?; echo "ERROR: build-uboot.sh failed at line ${BASH_LINENO[0]}: ${BASH_COMMAND} (rc=${rc})" >&2' ERR

usage() {
    cat <<'EOF'
Usage: build-uboot.sh HOST_DIR BOARD_DIR IMAGES_DIR UBOOT_DEFCONFIG FIP_TARGET UBOOT_TARGET

Downloads a cached U-Boot 2025.01, reapplies the AmLogic S905 patch set,
and runs LibreELEC's amlogic-boot-fip helper to populate imager-specific
subtrees under IMAGES_DIR/uboot-<target>.
EOF
}

if [ "$#" -ne 6 ]; then
    usage
    exit 1
fi

HOST_DIR=$1
BOARD_DIR=$2
IMAGES_DIR=$3
UBOOT_DEFCONFIG=$4
FIP_TARGET=$5
UBOOT_TARGET=$6

BOARD_NAME="$(basename "${BOARD_DIR}")"

: "${BR2_EXTERNAL_REGLINUX_PATH:?BR2_EXTERNAL_REGLINUX_PATH must be set}"

readonly UBOOT_VERSION=2025.01
readonly CACHE_DIR="${IMAGES_DIR}/build-uboot-cache"
readonly TARBALL="${CACHE_DIR}/u-boot-${UBOOT_VERSION}.tar.bz2"
readonly SOURCE_CACHE="${CACHE_DIR}/u-boot-${UBOOT_VERSION}"
readonly FIP_CACHE="${CACHE_DIR}/amlogic-boot-fip"

apply_patch_dir() {
    local dir="$1"
    if [ ! -d "${dir}" ]; then
        return
    fi

    for patch in "${dir}"/*.patch; do
        [ -e "${patch}" ] || continue
        echo "Applying patch: ${patch}"

        local log
        log="$(mktemp)"
        if ! patch -p1 < "${patch}" >"${log}" 2>&1; then
            echo "Patch ${patch} failed; log follows:"
            cat "${log}"
            rm -f "${log}"
            git status -sb || true
            exit 1
        fi
        rm -f "${log}"
    done
}

mkdir -p "${CACHE_DIR}"

if [ ! -f "${TARBALL}" ]; then
    echo "Downloading U-Boot ${UBOOT_VERSION}"
    wget -q -O "${TARBALL}" "https://ftp.denx.de/pub/u-boot/u-boot-${UBOOT_VERSION}.tar.bz2"
fi

if [ ! -d "${SOURCE_CACHE}" ]; then
    tar -xjf "${TARBALL}" -C "${CACHE_DIR}"
fi

if [ ! -d "${FIP_CACHE}" ]; then
    git clone --depth 1 https://github.com/LibreELEC/amlogic-boot-fip "${FIP_CACHE}"
fi

WORK_DIR="$(pwd)"
rm -rf "${WORK_DIR}/u-boot-${UBOOT_VERSION}"
cp -a "${SOURCE_CACHE}" "${WORK_DIR}"
UBOOT_SRC="${WORK_DIR}/u-boot-${UBOOT_VERSION}"

rm -rf "${UBOOT_SRC}/amlogic-boot-fip"
ln -s "${FIP_CACHE}" "${UBOOT_SRC}/amlogic-boot-fip"

echo "Building ${BOARD_NAME} with ${UBOOT_DEFCONFIG}"

pushd "${UBOOT_SRC}" >/dev/null
apply_patch_dir "${BR2_EXTERNAL_REGLINUX_PATH}/board/amlogic/s905/patches/uboot"
apply_patch_dir "${BOARD_DIR}/patches/uboot"

export CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-musl-"
echo "Running ARCH=aarch64 make ${UBOOT_DEFCONFIG}"
ARCH=aarch64 make "${UBOOT_DEFCONFIG}"
echo "Running ARCH=aarch64 make -j$(nproc)"
ARCH=aarch64 make -j"$(nproc)"
popd >/dev/null

RESULT_DIR="$(dirname "${IMAGES_DIR}")/uboot-${UBOOT_TARGET}"
mkdir -p "${RESULT_DIR}"

cp "${UBOOT_SRC}/u-boot.bin" "${RESULT_DIR}/u-boot.raw"

pushd "${UBOOT_SRC}/amlogic-boot-fip" >/dev/null
echo "Running build-fip.sh ${FIP_TARGET}"
./build-fip.sh "${FIP_TARGET}" "${UBOOT_SRC}/u-boot.bin" "${RESULT_DIR}/"
popd >/dev/null

if [ -f "${RESULT_DIR}/u-boot.bin" ]; then
    cp "${RESULT_DIR}/u-boot.bin" "${RESULT_DIR}/u-boot.bin.sd.bin"
fi
