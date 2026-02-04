#!/bin/bash
set -euo pipefail

usage() {
    cat <<EOF
Usage: $0 HOST_DIR BOARD_DIR BINARIES_DIR IMAGES_DIR UBOOT_DEFCONFIG UBOOT_TARGET

Compiles U-Boot 2025.01 for an Allwinner sun50i (H5/H6) board, rebuilds ARM
Trusted Firmware for the matching SoC, and stages u-boot-sunxi-with-spl.bin
under \${IMAGES_DIR}/uboot-\${UBOOT_TARGET}/.
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

SOC_DIR="$(cd "$(dirname "${BOARD_DIR}")" && pwd)"
SOC_NAME="$(basename "${SOC_DIR}")"
BOARD_NAME="$(basename "${BOARD_DIR}")"

default_atf_platform=""
case "${BOARD_NAME}" in
    orangepi-3|orangepi-3-lts|orangepi-one-plus)
        default_atf_platform="sun50i_h6"
        ;;
    orangepi-pc2|tritium-h5)
        default_atf_platform="sun50i_a64"
        ;;
esac

if [ -z "${UBOOT_ATF_PLATFORM:-}" ] && [ -z "${default_atf_platform}" ]; then
    echo "ERROR: Unknown sun50i board directory '${BOARD_NAME}'. Set UBOOT_ATF_PLATFORM." >&2
    exit 1
fi

readonly UBOOT_VERSION=2025.01
readonly TOOLCHAIN_PREFIX="${HOST_DIR}/bin/aarch64-buildroot-linux-musl-"
readonly BUILDROOT_DIR="${BR2_EXTERNAL_REGLINUX_PATH}/buildroot"

readonly ATF_GIT_URL="https://git.trustedfirmware.org/TF-A/trusted-firmware-a.git"
readonly ATF_VERSION="lts-v2.10.12"
readonly ATF_PLATFORM="${UBOOT_ATF_PLATFORM:-${default_atf_platform}}"
readonly ATF_ARCH="${UBOOT_ATF_ARCH:-aarch64}"
readonly ATF_BUILD_VARIANT="${UBOOT_ATF_VARIANT:-release}"
readonly ATF_BUILD_TARGET="${UBOOT_ATF_TARGET:-bl31}"
readonly ATF_PATCH_DIR="${UBOOT_ATF_PATCH_DIR:-${SOC_DIR}/patches/arm-trusted-firmware}"

echo "Using ATF platform: ${ATF_PLATFORM}"

if [ ! -x "${TOOLCHAIN_PREFIX}gcc" ]; then
    echo "ERROR: ${TOOLCHAIN_PREFIX}gcc is missing; run a full Buildroot build first." >&2
    exit 1
fi

if [ ! -d "${BUILDROOT_DIR}/support/kconfig" ]; then
    echo "ERROR: ${BUILDROOT_DIR}/support/kconfig is missing (is Buildroot checked out?)." >&2
    exit 1
fi

RESULT_BASE="${IMAGES_DIR}"
CACHE_DIR="${RESULT_BASE}/build-uboot-cache"
TARBALL="${CACHE_DIR}/u-boot-${UBOOT_VERSION}.tar.bz2"
SOURCE_CACHE="${CACHE_DIR}/u-boot-${UBOOT_VERSION}"
ATF_CACHE_DIR="${CACHE_DIR}/trusted-firmware-a-${ATF_VERSION}"

mkdir -p "${CACHE_DIR}"

if [ ! -f "${TARBALL}" ]; then
    echo "Downloading U-Boot ${UBOOT_VERSION}"
    wget -O "${TARBALL}" "https://ftp.denx.de/pub/u-boot/u-boot-${UBOOT_VERSION}.tar.bz2"
fi

if [ ! -d "${SOURCE_CACHE}" ]; then
    tar -xjf "${TARBALL}" -C "${CACHE_DIR}"
fi

WORK_DIR="$(pwd)"
UBOOT_SRC="${WORK_DIR}/u-boot-${UBOOT_VERSION}"
UBOOT_BUILD_DIR="${WORK_DIR}/build-${UBOOT_TARGET}"

prepare_atf_sources() {
    if [ -d "${ATF_CACHE_DIR}/.git" ]; then
        return 0
    fi
    echo "Cloning TF-A ${ATF_VERSION}"
    git clone --depth 1 --branch "${ATF_VERSION}" "${ATF_GIT_URL}" "${ATF_CACHE_DIR}"
}

build_atf() {
    prepare_atf_sources

    local atf_src="${WORK_DIR}/trusted-firmware-a-${UBOOT_TARGET}"
    rm -rf "${atf_src}"
    cp -a "${ATF_CACHE_DIR}" "${atf_src}"

    if [ -d "${ATF_PATCH_DIR}" ]; then
        for patch in "${ATF_PATCH_DIR}"/*.patch; do
            [ -e "${patch}" ] || continue
            echo "Applying TF-A patch: ${patch}"
            patch -d "${atf_src}" -p1 < "${patch}"
        done
    fi

    pushd "${atf_src}" >/dev/null
    local -a atf_make_opts
    atf_make_opts+=("CROSS_COMPILE=${TOOLCHAIN_PREFIX}")
    atf_make_opts+=("PLAT=${ATF_PLATFORM}")
    atf_make_opts+=("ARCH=${ATF_ARCH}")
    atf_make_opts+=("ARM_ARCH_MAJOR=8")
    atf_make_opts+=("BUILD_STRING=${ATF_VERSION}")

    make "${atf_make_opts[@]}" "${ATF_BUILD_TARGET}"
    popd >/dev/null

    local atf_img_dir="${atf_src}/build/${ATF_PLATFORM}/${ATF_BUILD_VARIANT}"
    local atf_bin="bl31"
    if [ ! -f "${atf_img_dir}/${atf_bin}.bin" ]; then
        echo "ERROR: TF-A build did not produce ${atf_bin}.bin" >&2
        exit 1
    fi

    mkdir -p "${BINARIES_DIR}"
    cp "${atf_img_dir}/${atf_bin}.bin" "${BINARIES_DIR}/${atf_bin}.bin"
    if [ -f "${atf_img_dir}/${atf_bin}.elf" ]; then
        cp "${atf_img_dir}/${atf_bin}.elf" "${BINARIES_DIR}/${atf_bin}.elf"
    fi
}

rm -rf "${UBOOT_SRC}" "${UBOOT_BUILD_DIR}"
cp -a "${SOURCE_CACHE}" "${UBOOT_SRC}"

apply_patch_dir() {
    local dir="$1"
    [ -d "${dir}" ] || return 0
    for patch in "${dir}"/*.patch; do
        [ -e "${patch}" ] || continue
        echo "Applying patch: ${patch}"
        patch -d "${UBOOT_SRC}" -p1 < "${patch}"
    done
}

COMMON_PATCH_DIR="${SOC_DIR}/patches/u-boot"
BOARD_PATCH_DIR="${BOARD_DIR}/patches/uboot"

apply_patch_dir "${COMMON_PATCH_DIR}"
apply_patch_dir "${BOARD_PATCH_DIR}"

build_atf

declare -a CONFIG_FRAGMENTS
COMMON_FRAGMENT="${SOC_DIR}/uboot.config.fragment"
[ -f "${COMMON_FRAGMENT}" ] && CONFIG_FRAGMENTS+=("${COMMON_FRAGMENT}")

BOARD_FRAGMENT="${BOARD_DIR}/uboot.config.fragment"
[ -f "${BOARD_FRAGMENT}" ] && CONFIG_FRAGMENTS+=("${BOARD_FRAGMENT}")

declare -a ATF_ARGS
detect_atf_blob() {
    local var="$1"
    shift
    local candidate
    for candidate in "$@"; do
        if [ -f "${BINARIES_DIR}/${candidate}" ]; then
            ATF_ARGS+=("${var}=${BINARIES_DIR}/${candidate}")
            echo "Using ${var}=${BINARIES_DIR}/${candidate}"
            return 0
        fi
    done
    return 1
}

detect_atf_blob "BL31" bl31.bin bl31.elf || {
    echo "ERROR: BL31 payload not found after TF-A build" >&2
    exit 1
}
ATF_ARGS+=("SCP=/dev/null")

NPROC=$(nproc 2>/dev/null || echo 1)

pushd "${UBOOT_SRC}" >/dev/null

ARCH=aarch64 CROSS_COMPILE="${TOOLCHAIN_PREFIX}" \
    make O="${UBOOT_BUILD_DIR}" "${ATF_ARGS[@]}" "${UBOOT_DEFCONFIG}"

if [ "${#CONFIG_FRAGMENTS[@]}" -gt 0 ]; then
    "${BUILDROOT_DIR}/support/kconfig/merge_config.sh" -m \
        -O "${UBOOT_BUILD_DIR}" "${UBOOT_BUILD_DIR}/.config" "${CONFIG_FRAGMENTS[@]}"
    ARCH=aarch64 CROSS_COMPILE="${TOOLCHAIN_PREFIX}" \
        make O="${UBOOT_BUILD_DIR}" "${ATF_ARGS[@]}" olddefconfig
fi

ARCH=aarch64 CROSS_COMPILE="${TOOLCHAIN_PREFIX}" \
    make -j"${NPROC}" O="${UBOOT_BUILD_DIR}" "${ATF_ARGS[@]}"

popd >/dev/null

UBOOT_BIN="${UBOOT_BUILD_DIR}/u-boot-sunxi-with-spl.bin"
if [ ! -f "${UBOOT_BIN}" ]; then
    echo "ERROR: ${UBOOT_BIN} not found after build" >&2
    exit 1
fi

DEST_DIR="${RESULT_BASE}/uboot-${UBOOT_TARGET}"
mkdir -p "${DEST_DIR}"
cp "${UBOOT_BIN}" "${DEST_DIR}/u-boot-sunxi-with-spl.bin"
