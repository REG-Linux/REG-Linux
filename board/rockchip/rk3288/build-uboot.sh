#!/bin/bash
set -euo pipefail

trap 'rc=$?; echo "ERROR: build-uboot.sh failed at line ${BASH_LINENO[0]}: ${BASH_COMMAND} (rc=${rc})" >&2' ERR

usage() {
    cat <<'EOF'
Usage: build-uboot.sh HOST_DIR BOARD_DIR BINARIES_DIR IMAGES_DIR UBOOT_DEFCONFIG UBOOT_TARGET

Builds U-Boot 2025.01 for RK3288 boards during the post-image step. The helper
downloads the upstream tarball once, applies the RK3288 patch queue, rebuilds
TF-A (BL32 sp_min) locally, and stages idbloader.img/u-boot.img under
${IMAGES_DIR}/uboot-${UBOOT_TARGET}/ so genimage can pack them.
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

readonly ATF_GIT_URL="https://git.trustedfirmware.org/TF-A/trusted-firmware-a.git"
readonly ATF_VERSION="lts-v2.10.12"
readonly ATF_PLATFORM="rk3288"
readonly ATF_BUILD_VARIANT="release"
readonly ATF_BUILD_TARGET="bl32"

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
            arm*-linux*-gcc)
                echo "$(normalize_prefix "${candidate%-gcc}")"
                return 0
                ;;
        esac
    done
    return 1
}

TOOLCHAIN_PREFIX="$(detect_toolchain_prefix || true)"
if [ -z "${TOOLCHAIN_PREFIX}" ]; then
    echo "ERROR: unable to locate an arm Linux cross-compiler under ${HOST_DIR}/bin (set CROSS_COMPILE?)." >&2
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
ATF_CACHE_DIR="${CACHE_DIR}/trusted-firmware-a-${ATF_VERSION}"

mkdir -p "${CACHE_DIR}"

if [ ! -f "${TARBALL}" ]; then
    echo "Downloading U-Boot ${UBOOT_VERSION}"
    wget -q -O "${TARBALL}" "https://ftp.denx.de/pub/u-boot/u-boot-${UBOOT_VERSION}.tar.bz2"
fi

if [ ! -d "${SOURCE_CACHE}" ]; then
    tar -xjf "${TARBALL}" -C "${CACHE_DIR}"
fi

prepare_atf_sources() {
    if [ -d "${ATF_CACHE_DIR}/.git" ]; then
        return 0
    fi
    echo "Cloning TF-A ${ATF_VERSION}"
    git clone --depth 1 --branch "${ATF_VERSION}" "${ATF_GIT_URL}" "${ATF_CACHE_DIR}"
}

build_atf() {
    prepare_atf_sources

    local atf_src="${PWD}/trusted-firmware-a-${UBOOT_TARGET}"
    rm -rf "${atf_src}"
    cp -a "${ATF_CACHE_DIR}" "${atf_src}"

    pushd "${atf_src}" >/dev/null
    local -a atf_make_opts
    atf_make_opts+=("CROSS_COMPILE=${TOOLCHAIN_PREFIX}")
    atf_make_opts+=("PLAT=${ATF_PLATFORM}")
    atf_make_opts+=("ARCH=aarch32")
    atf_make_opts+=("AARCH32_SP=sp_min")
    atf_make_opts+=("BUILD_STRING=${ATF_VERSION}")
    make "${atf_make_opts[@]}" "${ATF_BUILD_TARGET}"
    popd >/dev/null

    local atf_img_dir="${atf_src}/build/${ATF_PLATFORM}/${ATF_BUILD_VARIANT}/bl32"
    if [ ! -d "${atf_img_dir}" ]; then
        echo "ERROR: TF-A build output ${atf_img_dir} missing" >&2
        exit 1
    fi

    mkdir -p "${BINARIES_DIR}"
    cp "${atf_img_dir}/bl32.elf" "${BINARIES_DIR}/bl32.elf"
    if [ -f "${atf_img_dir}/bl32.bin" ]; then
        cp "${atf_img_dir}/bl32.bin" "${BINARIES_DIR}/bl32.bin"
    fi
}

WORK_DIR="$(pwd)"
rm -rf "${WORK_DIR}/u-boot-${UBOOT_VERSION}"
cp -a "${SOURCE_CACHE}" "${WORK_DIR}"
UBOOT_SRC="${WORK_DIR}/u-boot-${UBOOT_VERSION}"
UBOOT_BUILD_DIR="${WORK_DIR}/build-${UBOOT_TARGET}"

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

# Build TF-A first so the BL32 payload exists before the U-Boot pass.
build_atf

declare -a CONFIG_FRAGMENTS=()
if [ -f "${SOC_DIR}/uboot.config.fragment" ]; then
    CONFIG_FRAGMENTS+=("${SOC_DIR}/uboot.config.fragment")
fi
if [ -f "${BOARD_DIR}/uboot.config.fragment" ]; then
    CONFIG_FRAGMENTS+=("${BOARD_DIR}/uboot.config.fragment")
fi

declare -a ATF_ARGS=()
if [ -f "${BINARIES_DIR}/bl32.elf" ]; then
    ATF_ARGS+=("BL32=${BINARIES_DIR}/bl32.elf")
elif [ -f "${BINARIES_DIR}/bl32.bin" ]; then
    ATF_ARGS+=("BL32=${BINARIES_DIR}/bl32.bin")
else
    echo "ERROR: Missing bl32.{elf,bin} payload" >&2
    exit 1
fi

NPROC=$(nproc 2>/dev/null || echo 1)

pushd "${UBOOT_SRC}" >/dev/null
ARCH=arm CROSS_COMPILE="${TOOLCHAIN_PREFIX}" \
    make O="${UBOOT_BUILD_DIR}" "${ATF_ARGS[@]}" "${UBOOT_DEFCONFIG}"

if [ "${#CONFIG_FRAGMENTS[@]}" -gt 0 ]; then
    "${BUILDROOT_DIR}/support/kconfig/merge_config.sh" -m \
        -O "${UBOOT_BUILD_DIR}" "${UBOOT_BUILD_DIR}/.config" "${CONFIG_FRAGMENTS[@]}"
    ARCH=arm CROSS_COMPILE="${TOOLCHAIN_PREFIX}" \
        make O="${UBOOT_BUILD_DIR}" "${ATF_ARGS[@]}" olddefconfig
fi

ARCH=arm CROSS_COMPILE="${TOOLCHAIN_PREFIX}" \
    make -j"${NPROC}" O="${UBOOT_BUILD_DIR}" "${ATF_ARGS[@]}"
popd >/dev/null

for artifact in idbloader.img u-boot.img; do
    if [ ! -f "${UBOOT_BUILD_DIR}/${artifact}" ]; then
        echo "ERROR: ${UBOOT_BUILD_DIR}/${artifact} missing after build" >&2
        exit 1
    fi
done

DEST_DIR="${RESULT_BASE}/uboot-${UBOOT_TARGET}"
mkdir -p "${DEST_DIR}"
cp "${UBOOT_BUILD_DIR}/idbloader.img" "${DEST_DIR}/idbloader.img"
cp "${UBOOT_BUILD_DIR}/u-boot.img" "${DEST_DIR}/u-boot.img"
