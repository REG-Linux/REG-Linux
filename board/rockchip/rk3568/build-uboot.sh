#!/bin/bash
set -euo pipefail

trap 'rc=$?; echo "ERROR: build-uboot.sh failed at line ${BASH_LINENO[0]}: ${BASH_COMMAND} (rc=${rc})" >&2' ERR

usage() {
    cat <<'EOF'
Usage: build-uboot.sh HOST_DIR BOARD_DIR REGLINUX_BINARIES_DIR UBOOT_DEFCONFIG UBOOT_TARGET

Downloads a cached U-Boot 2025.10, patches it with the RK3568 set, and builds
each target with LibreELEC's rkbin blobs. Outputs land in
REGLINUX_BINARIES_DIR/../uboot-<target>/.
EOF
}

if [ "$#" -ne 5 ]; then
    usage
    exit 1
fi

HOST_DIR=$1
BOARD_DIR=$2
REGLINUX_BINARIES_DIR=$3
UBOOT_DEFCONFIG=$4
UBOOT_TARGET=$5

readonly UBOOT_VERSION=2025.10
readonly RKBIN_COMMIT=7c35e21a8529b3758d1f051d1a5dc62aae934b2b
readonly CACHE_DIR="${REGLINUX_BINARIES_DIR}/../build-uboot-cache"
readonly TARBALL="${CACHE_DIR}/u-boot-${UBOOT_VERSION}.tar.bz2"
readonly SOURCE_CACHE="${CACHE_DIR}/u-boot-${UBOOT_VERSION}"
readonly RKBIN_CACHE="${CACHE_DIR}/rkbin"

apply_patch_dir() {
    local dir="$1"
    [ -d "${dir}" ] || return 0
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

if [ ! -d "${RKBIN_CACHE}" ]; then
    git clone https://github.com/rockchip-linux/rkbin "${RKBIN_CACHE}"
fi

git -C "${RKBIN_CACHE}" fetch --depth=1 origin "${RKBIN_COMMIT}" >/dev/null 2>&1 || true
git -C "${RKBIN_CACHE}" checkout --force "${RKBIN_COMMIT}"
git -C "${RKBIN_CACHE}" reset --hard "${RKBIN_COMMIT}"

WORK_DIR="$(pwd)"
rm -rf "${WORK_DIR}/u-boot-${UBOOT_VERSION}"
cp -a "${SOURCE_CACHE}" "${WORK_DIR}"
UBOOT_SRC="${WORK_DIR}/u-boot-${UBOOT_VERSION}"

echo "Building ${UBOOT_TARGET} (${UBOOT_DEFCONFIG}) with U-Boot ${UBOOT_VERSION}"

pushd "${UBOOT_SRC}" >/dev/null
apply_patch_dir "${BR2_EXTERNAL_REGLINUX_PATH}/board/rockchip/rk3568/patches/uboot"
apply_patch_dir "${BOARD_DIR}/patches/uboot"

export BL31="${RKBIN_CACHE}/bin/rk35/rk3568_bl31_v1.44.elf"
export ROCKCHIP_TPL="${RKBIN_CACHE}/bin/rk35/rk3568_ddr_1056MHz_v1.23.bin"
export CROSS_COMPILE="${HOST_DIR}/bin/aarch64-buildroot-linux-gnu-"
echo "Running ARCH=aarch64 make ${UBOOT_DEFCONFIG}"
ARCH=aarch64 make "${UBOOT_DEFCONFIG}"
echo "Running ARCH=aarch64 make -j$(nproc)"
ARCH=aarch64 make -j"$(nproc)"
popd >/dev/null

RESULT_DIR="$(dirname "${REGLINUX_BINARIES_DIR}")/uboot-${UBOOT_TARGET}"
mkdir -p "${RESULT_DIR}"
cp "${UBOOT_SRC}/u-boot-rockchip.bin" "${RESULT_DIR}/u-boot-rockchip.bin"
[ -f "${UBOOT_SRC}/u-boot.itb" ] && cp "${UBOOT_SRC}/u-boot.itb" "${RESULT_DIR}/u-boot.itb"
