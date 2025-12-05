#!/bin/bash
set -euo pipefail

trap 'rc=$?; echo "ERROR: build-uboot.sh failed at line ${BASH_LINENO[0]}: ${BASH_COMMAND} (rc=${rc})" >&2' ERR

usage() {
    cat <<'EOF'
Usage: build-uboot.sh HOST_DIR BOARD_DIR BINARIES_DIR IMAGES_DIR UBOOT_DEFCONFIG UBOOT_TARGET

Builds U-Boot 2025.01 for RK3328 boards during the post-image step. The helper
caches the upstream U-Boot tarball and Rockchip rkbin repository, applies any
SoC/board patch queues, wires in the rkbin BL31/TPL blobs, and stages
u-boot-rockchip.bin under ${IMAGES_DIR}/uboot-${UBOOT_TARGET}/ for genimage.
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

readonly SOC_DIR="$(dirname "${BOARD_DIR}")"
readonly UBOOT_VERSION=2025.01
readonly BUILDROOT_DIR="${BR2_EXTERNAL_REGLINUX_PATH}/buildroot"
readonly RKBIN_URL="https://github.com/rockchip-linux/rkbin.git"
readonly RKBIN_COMMIT="74213af1e952c4683d2e35952507133b61394862"
readonly ATF_GIT_URL="https://git.trustedfirmware.org/TF-A/trusted-firmware-a.git"
readonly ATF_VERSION="lts-v2.10.12"
readonly ATF_PLATFORM="rk3328"

normalize_prefix() {
    local prefix="$1"
    case "${prefix}" in
        *-) echo "${prefix}" ;;
        *) echo "${prefix}-" ;;
    esac
}

detect_toolchain_prefix() {
    if [ -n "${CROSS_COMPILE:-}" ] && command -v "${CROSS_COMPILE}gcc" >/dev/null 2>&1; then
        echo "$(normalize_prefix "${CROSS_COMPILE}")"
        return 0
    fi
    local candidate base
    for candidate in "${HOST_DIR}/bin/"*-gcc; do
        [ -x "${candidate}" ] || continue
        base="$(basename "${candidate}")"
        case "${base}" in
            aarch64*-linux*-gcc)
                echo "$(normalize_prefix "${candidate%-gcc}")"
                return 0
                ;;
        esac
    done
    return 1
}

TOOLCHAIN_PREFIX="$(detect_toolchain_prefix || true)"
if [ -z "${TOOLCHAIN_PREFIX}" ]; then
    echo "ERROR: unable to locate an aarch64 cross-compiler under ${HOST_DIR}/bin (set CROSS_COMPILE?)." >&2
    exit 1
fi
readonly TOOLCHAIN_PREFIX

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
RKBIN_CACHE="${CACHE_DIR}/rkbin"

mkdir -p "${CACHE_DIR}"

if [ ! -f "${TARBALL}" ]; then
    echo "Downloading U-Boot ${UBOOT_VERSION}"
    wget -q -O "${TARBALL}" "https://ftp.denx.de/pub/u-boot/u-boot-${UBOOT_VERSION}.tar.bz2"
fi

if [ ! -d "${SOURCE_CACHE}" ]; then
    tar -xjf "${TARBALL}" -C "${CACHE_DIR}"
fi

if [ ! -d "${RKBIN_CACHE}" ]; then
    git clone "${RKBIN_URL}" "${RKBIN_CACHE}"
fi

git -C "${RKBIN_CACHE}" fetch --depth=1 origin "${RKBIN_COMMIT}" >/dev/null 2>&1 || true
git -C "${RKBIN_CACHE}" checkout --force "${RKBIN_COMMIT}" >/dev/null
git -C "${RKBIN_CACHE}" reset --hard "${RKBIN_COMMIT}" >/dev/null

WORK_DIR="$(pwd)"
rm -rf "${WORK_DIR}/u-boot-${UBOOT_VERSION}"
cp -a "${SOURCE_CACHE}" "${WORK_DIR}"
UBOOT_SRC="${WORK_DIR}/u-boot-${UBOOT_VERSION}"
UBOOT_BUILD_DIR="${WORK_DIR}/build-${UBOOT_TARGET}"
ATF_CACHE_DIR="${CACHE_DIR}/trusted-firmware-a-${ATF_VERSION}"

prepare_atf_sources() {
    if [ -d "${ATF_CACHE_DIR}/.git" ]; then
        return 0
    fi
    echo "Cloning TF-A ${ATF_VERSION}" >&2
    git clone --depth 1 --branch "${ATF_VERSION}" "${ATF_GIT_URL}" "${ATF_CACHE_DIR}" >&2
}

build_atf() {
    prepare_atf_sources

    local atf_src="${WORK_DIR}/trusted-firmware-a-${UBOOT_TARGET}"
    rm -rf "${atf_src}"
    cp -a "${ATF_CACHE_DIR}" "${atf_src}"

    pushd "${atf_src}" >/dev/null
    {
        make CROSS_COMPILE="${TOOLCHAIN_PREFIX}" PLAT="${ATF_PLATFORM}" \
            BUILD_STRING="${ATF_VERSION}" bl31
    } >&2
    popd >/dev/null

    local bl31_path="${atf_src}/build/${ATF_PLATFORM}/release/bl31/bl31.elf"
    if [ ! -f "${bl31_path}" ]; then
        echo "ERROR: TF-A build did not produce ${bl31_path}" >&2
        exit 1
    fi
    printf '%s\n' "${bl31_path}"
}

apply_patch_dir() {
    local dir="$1"
    [ -d "${dir}" ] || return 0
    for patch in "${dir}"/*.patch; do
        [ -e "${patch}" ] || continue
        echo "Applying patch: ${patch}"
        local log
        log="$(mktemp)"
        if ! patch -d "${UBOOT_SRC}" -p1 < "${patch}" >"${log}" 2>&1; then
            echo "Patch ${patch} failed; log follows:"
            cat "${log}"
            rm -f "${log}"
            exit 1
        fi
        rm -f "${log}"
    done
}

COMMON_PATCH_DIR="${SOC_DIR}/patches/uboot"
BOARD_PATCH_DIR="${BOARD_DIR}/patches/uboot"
apply_patch_dir "${COMMON_PATCH_DIR}"
apply_patch_dir "${BOARD_PATCH_DIR}"

BL31_PATH="$(build_atf)"

declare -a CONFIG_FRAGMENTS=()
if [ -f "${SOC_DIR}/uboot.config.fragment" ]; then
    CONFIG_FRAGMENTS+=("${SOC_DIR}/uboot.config.fragment")
fi
if [ -f "${BOARD_DIR}/uboot.config.fragment" ]; then
    CONFIG_FRAGMENTS+=("${BOARD_DIR}/uboot.config.fragment")
fi

NPROC=$(nproc 2>/dev/null || echo 1)

pushd "${UBOOT_SRC}" >/dev/null

BL31="${BL31_PATH}" ROCKCHIP_TPL="${RKBIN_CACHE}/bin/rk33/rk3328_ddr_400MHz_v1.21.bin" \
    CROSS_COMPILE="${TOOLCHAIN_PREFIX}" ARCH=aarch64 \
    make O="${UBOOT_BUILD_DIR}" "${UBOOT_DEFCONFIG}"

if [ "${#CONFIG_FRAGMENTS[@]}" -gt 0 ]; then
    "${BUILDROOT_DIR}/support/kconfig/merge_config.sh" -m \
        -O "${UBOOT_BUILD_DIR}" "${UBOOT_BUILD_DIR}/.config" "${CONFIG_FRAGMENTS[@]}"
    BL31="${BL31_PATH}" ROCKCHIP_TPL="${RKBIN_CACHE}/bin/rk33/rk3328_ddr_400MHz_v1.21.bin" \
        CROSS_COMPILE="${TOOLCHAIN_PREFIX}" ARCH=aarch64 \
        make O="${UBOOT_BUILD_DIR}" olddefconfig
fi

BL31="${BL31_PATH}" ROCKCHIP_TPL="${RKBIN_CACHE}/bin/rk33/rk3328_ddr_400MHz_v1.21.bin" \
    CROSS_COMPILE="${TOOLCHAIN_PREFIX}" ARCH=aarch64 \
    make -j"${NPROC}" O="${UBOOT_BUILD_DIR}"

popd >/dev/null

if [ ! -f "${UBOOT_BUILD_DIR}/u-boot-rockchip.bin" ]; then
    echo "ERROR: ${UBOOT_BUILD_DIR}/u-boot-rockchip.bin missing after build" >&2
    exit 1
fi

DEST_DIR="${RESULT_BASE}/uboot-${UBOOT_TARGET}"
mkdir -p "${DEST_DIR}"
cp "${UBOOT_BUILD_DIR}/u-boot-rockchip.bin" "${DEST_DIR}/u-boot-rockchip.bin"
