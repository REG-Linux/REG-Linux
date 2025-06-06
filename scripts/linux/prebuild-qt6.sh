#!/bin/sh

# Run this script from root directory of the project like
# ./scripts/linux/prebuild-qt6.sh

if [ "$1" != "" ]; then
    ARCHS=$*
else
    ARCHS="rk3288 h5 bcm2711 bcm2712 rk3326 rk3399 rk3588 s905gen3 s922x sm8250 saphira jh7110 k1 x86_64 x86_64_v3"
fi

# Grab QT6 version from source tree
QT6_VERSION="$(cat <package/libraries/reglinux-qt6/reglinux-qt6.mk | grep REGLINUX_QT6_VERSION | cut -d " " -f 3 | head -n1)"

echo "Building REG-Linux QT6 v${QT6_VERSION} for ${ARCHS}"

# Create prebuilt output directory
mkdir -p prebuilt

# Enable the flag to build QT6 from source
sed -i s/#BR2_PACKAGE_REGLINUX_QT6=y/BR2_PACKAGE_REGLINUX_QT6=y/ configs/reglinux-board.common
sed -i s/#BR2_PACKAGE_REGLINUX_QT6_BUILD_FROM_SOURCE=y/BR2_PACKAGE_REGLINUX_QT6_BUILD_FROM_SOURCE=y/ configs/reglinux-board.common
sed -i s/#BR2_PACKAGE_QT6BASE_DEFAULT_QPA=\"wayland\"/BR2_PACKAGE_QT6BASE_DEFAULT_QPA=\"wayland\"/ configs/reglinux-board.common

# Loop over archs
# h5 can be used for h6, h616, s905, s905gen2, rk3328 (cortex_a53)
# rk3326 can be used for s9gen4 (cortex_a35)
# s922X can be used for a3gen2 (cortex_a73_a53)
# s905gen3 can be used for rk3566/rk3568 (cortex_a55)
# sm8250 can be used for sm8550 (vulkan)
for arch in ${ARCHS}; do
    # Clean
    make "${arch}"-clean
    # Build
    PKG=reglinux-qt6 make "${arch}"-pkg DEBUG_BUILD=n PARALLEL_BUILD=n
    # Package
    cd output/"${arch}" || exit 1
    staging="$(cat build/staging.dir)"
    cat build/host-qt6*/.files-list-host.txt | cut -d ',' -f 2 | sed -e 's/\.\//host\//g' >qt6-host-files.txt
    cat build/qt6*/.files-list-staging.txt | cut -d ',' -f 2 | sed -e "s+\.\/+$staging\/+g" >qt6-staging-files.txt
    cat build/qt6*/.files-list.txt | cut -d ',' -f 2 | sed -e 's/\.\//target\//g' >qt6-target-files.txt
    cat qt6-host-files.txt qt6-staging-files.txt qt6-target-files.txt >filelist.txt
    find . | grep /host/ | grep Qt >>filelist.txt
    find . | grep /target/ | grep Qt >>filelist.txt
    awk -i inplace '!seen[$0]++' filelist.txt
    tar cvzf ../../prebuilt/reglinux-qt6-"${QT6_VERSION}"-"${arch}".tar.gz -T filelist.txt
    cd ../..
    # Clean again
    make "${arch}"-clean
done

# Disable the flag to build QT6 from source
sed -i s/BR2_PACKAGE_REGLINUX_QT6=y/#BR2_PACKAGE_REGLINUX_QT6=y/ configs/reglinux-board.common
sed -i s/BR2_PACKAGE_REGLINUX_QT6_BUILD_FROM_SOURCE=y/#BR2_PACKAGE_REGLINUX_QT6_BUILD_FROM_SOURCE=y/ configs/reglinux-board.common
sed -i s/BR2_PACKAGE_QT6BASE_DEFAULT_QPA=\"wayland\"/#BR2_PACKAGE_QT6BASE_DEFAULT_QPA=\"wayland\"/ configs/reglinux-board.common
