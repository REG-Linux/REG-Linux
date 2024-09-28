#!/bin/sh

# Run this script from root directory of the project like
# ./scripts/linux/prebuild-scummvms.sh

# Grab ScummVM version from source tree
SCUMMVM_VERSION=$(cat package/emulators/scummvm/scummvm.mk | grep SCUMMVM_VERSION | cut -d "=" -f 2 | head -n1 | tr -d '[:space:]')
LRSCUMMVM_VERSION=$(cat package/emulators/retroarch/libretro/libretro-scummvm/libretro-scummvm.mk | grep LIBRETRO_SCUMMVM_VERSION | cut -d "=" -f 2 | head -n1 | tr -d '[:space:]')

# Check both version matches, or abort
if [ "$SCUMMVM_VERSION" != "$LRSCUMMVM_VERSION" ]
then
	echo "ScummVM $SCUMMVM_VERSION and libretro-scummvm $LRSCUMMVM_VERSION do not match, aborting"
	exit -1
fi

echo "Building ScummVM/lr-scummvmm combo version ($SCUMMVM_VERSION) for all archs"

# Create prebuilt output directory
mkdir -p prebuilt

# Enable the flag to build ScummVM from source
sed -i s/#BR2_PACKAGE_SCUMMVM_BUILD_FROM_SOURCE=y/BR2_PACKAGE_SCUMMVM_BUILD_FROM_SOURCE=y/ configs/batocera-board.common

# Loop over archs
# bcm2836 can be used for h3/cha and rk3128 (cortex_a7)
# rk3326 can be used for s9gen4 (cortex_a35)
# h5 can be used for h6, h616, s905, s905gen2, rk3328 (cortex_a53)
# s905gen3 can be used for rk3566/rk3568 (cortex_a55)
# s922x can be used for a3gen2 (cortex_a73_a53)
for arch in jz4770 bcm2835 bcm2836 s812 odroidxu4 rk3288 h5 bcm2711 bcm2712 rk3326 rk3399 rk3588 s905gen3 s922x saphira jh7110 k1 x86_64 x86_64_v3; do
	# Clean
	make ${arch}-clean
	# Build
	PKG=scummvm make ${arch}-pkg
	PKG=libretro-scummvm make ${arch}-pkg
	# Package
	cd output/${arch}/target
	tar cvzf ../../../prebuilt/reglinux-scummvm-${SCUMMVM_VERSION}-${arch}.tar.gz usr/bin/scummvm usr/lib/libretro/scummvm_libretro.so usr/share/scummvm usr/lib/scummvm
	cd ../../..
	# Clean again
	make ${arch}-clean
done

# Disable the flag to build ScummVM from source
sed -i s/BR2_PACKAGE_SCUMMVM_BUILD_FROM_SOURCE=y/#BR2_PACKAGE_SCUMMVM_BUILD_FROM_SOURCE=y/ configs/batocera-board.common

