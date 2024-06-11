#!/bin/sh

# Run this script from root directory of the project like
# ./scripts/linux/prebuild-mames.sh

# Grab MAME version from source tree
MAME_VERSION=$(cat package/batocera/emulators/mame/mame.mk | grep GroovyMAME | grep Version | cut -d " " -f 4)
LRMAME_VERSION=$(cat package/batocera/emulators/retroarch/libretro/libretro-mame/libretro-mame.mk | grep LIBRETRO_MAME_VERSION | grep lrmame | cut -d " " -f 3 | sed s/lrmame//g | sed s/0/0\./g)

# Check both version matches, or abort
if [ "$MAME_VERSION" != "$LRMAME_VERSION" ]
then
	echo "MAME $MAME_VERSION and libretro-mame $LRMAME_VERSION do not match, aborting"
	exit -1
fi

echo "Building MAME/lr-mame combo version ($MAME_VERSION) for all archs"

# Create prebuilt output directory
mkdir -p prebuilt

# Enable the flag to build MAME from source
sed -i s/#BR2_PACKAGE_MAME_BUILD_FROM_SOURCE=y/BR2_PACKAGE_MAME_BUILD_FROM_SOURCE=y/ configs/batocera-board.common

# Loop over archs
# rk3326 can be used for s9gen4 (cortex_a35)
# h5 can be used for h6, h616, s905, s905gen2, rk3328 (cortex_a53)
# s905gen3 can be used for rk3566/rk3568 (cortex_a55)
# s922x can be used for a3gen2 (cortex_a73_a53)
for arch in s812 odroidxu4 rk3288 h5 bcm2711 bcm2712 rk3326 rk3399 rk3588 s905gen3 s922x saphira visionfive2 bpif3 x86_64 x86_64_v3; do
	# Clean
	make ${arch}-clean
	# Build
	PKG=mame make ${arch}-pkg
	PKG=libretro-mame make ${arch}-pkg
	# Package
	cd output/${arch}/target
	tar cvzf ../../../prebuilt/reglinux-mame-${MAME_VERSION}-${arch}.tar.gz usr/bin/mame/ usr/lib/libretro/mame_libretro.so usr/share/mame/ usr/share/lr-mame/
	cd ../../..
	# Clean again
	make ${arch}-clean
done

# Disable the flag to build MAME from source
sed -i s/BR2_PACKAGE_MAME_BUILD_FROM_SOURCE=y/#BR2_PACKAGE_MAME_BUILD_FROM_SOURCE=y/ configs/batocera-board.common

