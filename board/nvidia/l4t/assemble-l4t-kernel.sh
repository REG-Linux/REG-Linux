#!/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later
#
# Assemble L4T kernel source tree from multiple git repositories
# This is a simplified version of Lakka-LibreELEC's get_l4t-kernel-sources
# script, targeting T210 (Tegra X1) only.
#
# Usage: ./board/nvidia/l4t/assemble-l4t-kernel.sh [output_dir]
#
# The assembled kernel source tree will be placed in <output_dir>/
# and a tarball will be created as dl/linux-l4t-4.9.tar.gz
# If output_dir is not specified, uses a temporary directory.

set -e

OUTPUT_DIR="${1:-$(mktemp -d)}"
DOWNLOAD_DIR="$(mktemp -d)"

# L4T kernel source repositories (T210 / Tegra X1)
L4T_KERNEL_4_9_REPO="https://github.com/CTCaer/switch-l4t-kernel-4.9.git"
L4T_KERNEL_4_9_BRANCH="linux-5.1.2"
L4T_KERNEL_4_9_SHA="2d0059fd3167a8df756de2aa0489d4aa70a9fc15"

L4T_KERNEL_NVIDIA_REPO="https://github.com/CTCaer/switch-l4t-kernel-nvidia.git"
L4T_KERNEL_NVIDIA_BRANCH="linux-5.1.2"
L4T_KERNEL_NVIDIA_SHA="a4cc21186653434c0362323b12354e6e713ad5af"

L4T_KERNEL_NVGPU_REPO="https://gitlab.com/switchroot/kernel/l4t-kernel-nvgpu.git"
L4T_KERNEL_NVGPU_BRANCH="linux-3.4.0-r32.5"
L4T_KERNEL_NVGPU_SHA="1ae0167d360287ca78f5a2572f0de42594140312"

L4T_SOC_TEGRA_REPO="https://gitlab.com/switchroot/kernel/l4t-soc-tegra.git"
L4T_SOC_TEGRA_BRANCH="l4t/l4t-r32.3.1"

L4T_PLATFORM_TEGRA_COMMON_REPO="https://gitlab.com/switchroot/kernel/l4t-platform-tegra-common.git"
L4T_PLATFORM_TEGRA_COMMON_BRANCH="l4t/l4t-r32.3.1"

L4T_PLATFORM_T210_COMMON_REPO="https://gitlab.com/switchroot/kernel/l4t-platform-t210-common.git"
L4T_PLATFORM_T210_COMMON_BRANCH="l4t/l4t-r32.3.1"

L4T_SOC_T210_REPO="https://gitlab.com/switchroot/kernel/l4t-soc-t210.git"
L4T_SOC_T210_BRANCH="l4t/l4t-r32.3.1"

L4T_PLATFORM_T210_NX_REPO="https://github.com/CTCaer/switch-l4t-platform-t210-nx.git"
L4T_PLATFORM_T210_NX_BRANCH="linux-dev"
L4T_PLATFORM_T210_NX_SHA="cf785c4c176499b301170d79fe57b77f365b73cd"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PATCH_DIR="${SCRIPT_DIR}/linux_patches"

cleanup() {
    rm -rf "${DOWNLOAD_DIR}"
}
trap cleanup EXIT

clone_repo() {
    local repo="$1"
    local branch="$2"
    local sha="$3"
    local name

    name="$(basename "${repo}" .git)"
    echo "Cloning ${name} (branch: ${branch})..."
    git clone -b "${branch}" --depth 1 "${repo}" "${DOWNLOAD_DIR}/${name}"
    if [ -n "${sha}" ]; then
        cd "${DOWNLOAD_DIR}/${name}"
        git fetch --unshallow 2>/dev/null || true
        git reset --hard "${sha}"
        cd "${DOWNLOAD_DIR}"
    fi
    rm -rf "${DOWNLOAD_DIR}/${name}/.git"*
}

echo "=== Assembling L4T kernel source tree ==="
echo "Output: ${OUTPUT_DIR}"

mkdir -p "${OUTPUT_DIR}"
cd "${DOWNLOAD_DIR}"

# 1. Clone base kernel
clone_repo "${L4T_KERNEL_4_9_REPO}" "${L4T_KERNEL_4_9_BRANCH}" "${L4T_KERNEL_4_9_SHA}"
cp -a "${DOWNLOAD_DIR}/switch-l4t-kernel-4.9/"* "${OUTPUT_DIR}/"
rm -rf "${DOWNLOAD_DIR}/switch-l4t-kernel-4.9"

# 2. NVIDIA kernel driver overlay
mkdir -p "${OUTPUT_DIR}/nvidia"
clone_repo "${L4T_KERNEL_NVIDIA_REPO}" "${L4T_KERNEL_NVIDIA_BRANCH}" "${L4T_KERNEL_NVIDIA_SHA}"
cp -a "${DOWNLOAD_DIR}/switch-l4t-kernel-nvidia/"* "${OUTPUT_DIR}/nvidia/"
rm -rf "${DOWNLOAD_DIR}/switch-l4t-kernel-nvidia"

# 3. NVGPU driver
mkdir -p "${OUTPUT_DIR}/nvidia/nvgpu"
clone_repo "${L4T_KERNEL_NVGPU_REPO}" "${L4T_KERNEL_NVGPU_BRANCH}" "${L4T_KERNEL_NVGPU_SHA}"
cp -a "${DOWNLOAD_DIR}/l4t-kernel-nvgpu/"* "${OUTPUT_DIR}/nvidia/nvgpu/"
rm -rf "${DOWNLOAD_DIR}/l4t-kernel-nvgpu"

# 4. Platform T210 common
mkdir -p "${OUTPUT_DIR}/nvidia/platform/t210/common"
clone_repo "${L4T_PLATFORM_T210_COMMON_REPO}" "${L4T_PLATFORM_T210_COMMON_BRANCH}" ""
cp -a "${DOWNLOAD_DIR}/l4t-platform-t210-common/"* "${OUTPUT_DIR}/nvidia/platform/t210/common/"
rm -rf "${DOWNLOAD_DIR}/l4t-platform-t210-common"

# 5. Platform tegra common
mkdir -p "${OUTPUT_DIR}/nvidia/platform/tegra/common"
clone_repo "${L4T_PLATFORM_TEGRA_COMMON_REPO}" "${L4T_PLATFORM_TEGRA_COMMON_BRANCH}" ""
cp -a "${DOWNLOAD_DIR}/l4t-platform-tegra-common/"* "${OUTPUT_DIR}/nvidia/platform/tegra/common/"
rm -rf "${DOWNLOAD_DIR}/l4t-platform-tegra-common"

# 6. SoC T210
mkdir -p "${OUTPUT_DIR}/nvidia/soc/t210/kernel-dts"
clone_repo "${L4T_SOC_T210_REPO}" "${L4T_SOC_T210_BRANCH}" ""
cp -a "${DOWNLOAD_DIR}/l4t-soc-t210/kernel-dts/"* "${OUTPUT_DIR}/nvidia/soc/t210/kernel-dts/"
rm -rf "${DOWNLOAD_DIR}/l4t-soc-t210"

# 7. SoC tegra kernel-include
mkdir -p "${OUTPUT_DIR}/nvidia/soc/tegra/kernel-include"
clone_repo "${L4T_SOC_TEGRA_REPO}" "${L4T_SOC_TEGRA_BRANCH}" ""
cp -a "${DOWNLOAD_DIR}/l4t-soc-tegra/kernel-include/"* "${OUTPUT_DIR}/nvidia/soc/tegra/kernel-include/"
rm -rf "${DOWNLOAD_DIR}/l4t-soc-tegra"

# 8. Custom board DTS (T210 NX platform)
mkdir -p "${OUTPUT_DIR}/nvidia/platform/t210/nx"
clone_repo "${L4T_PLATFORM_T210_NX_REPO}" "${L4T_PLATFORM_T210_NX_BRANCH}" "${L4T_PLATFORM_T210_NX_SHA}"
cp -a "${DOWNLOAD_DIR}/switch-l4t-platform-t210-nx/"* "${OUTPUT_DIR}/nvidia/platform/t210/nx/"
rm -rf "${DOWNLOAD_DIR}/switch-l4t-platform-t210-nx"

# 9. Apply unification patches
echo "=== Applying kernel unification patches ==="
cd "${OUTPUT_DIR}"
for patch in "${PATCH_DIR}"/*.patch; do
    if [ -f "${patch}" ]; then
        echo "Applying: $(basename "${patch}")"
        patch -p1 < "${patch}"
    fi
done

# 10. Create tarball for Buildroot
echo "=== Creating kernel source tarball ==="
# Detect project root (where this script lives under board/nvidia/l4t/)
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
TARBALL_DIR="${PROJECT_ROOT}/dl"
mkdir -p "${TARBALL_DIR}"
TARBALL_PATH="${TARBALL_DIR}/linux-l4t-4.9.tar.gz"

cd "${OUTPUT_DIR}"
tar -czf "${TARBALL_PATH}" .

echo "=== Done ==="
echo "Kernel source tree: ${OUTPUT_DIR}"
echo "Kernel tarball: ${TARBALL_PATH}"
echo ""
echo "The tarball is ready for Buildroot. You can now build with:"
echo "  make reglinux-l4t_defconfig && make"
