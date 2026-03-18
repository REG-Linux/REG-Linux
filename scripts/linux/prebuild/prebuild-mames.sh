#!/bin/sh

# Run this script from root directory of the project like
# ./scripts/linux/prebuild-mames.sh

# Grab MAME version from source tree
MAME_VERSION=$(cat package/emulators/mame/mame.mk | grep GroovyMAME | grep Version | cut -d " " -f 4)
#MAME_VERSION=$(cat package/emulators/mame/mame.mk | grep "Version: MAME" | cut -d " " -f 4)
LRMAME_VERSION=$(cat package/emulators/libretro/libretro-mame/libretro-mame.mk | grep LIBRETRO_MAME_VERSION | grep lrmame | cut -d " " -f 3 | sed s/lrmame//g | sed s/0/0\./)

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
sed -i s/#BR2_PACKAGE_MAME_BUILD_FROM_SOURCE=y/BR2_PACKAGE_MAME_BUILD_FROM_SOURCE=y/ configs/reglinux-board.common

# Loop over archs
# rk3326 can be used for s9gen4 (cortex_a35)
# h5 can be used for h6, h616, s905, s905gen2, rk3328 (cortex_a53)
# s905gen3 can be used for rk3566/rk3568 (cortex_a55)
# s922x can be used for a3gen2 (cortex_a73_a53)
# rk3588 can be used for sm8250 (cortex_a76_a55)
# jh7110 can be used for k1 (no vector extensions support however)
# DEPRECATED : ARM 32-bit targets : s812 odroidxu4 rk3288
for arch in h5 bcm2711 bcm2712 rk3326 rk3399 rk3588 s905gen3 s922x sm8550 asahi jh7110 k1 x86_64 x86_64_v3; do
	# Clean
	make ${arch}-clean
	# Build
	PKG=mame make ${arch}-pkg DEBUG_BUILD=n
	PKG=libretro-mame make ${arch}-pkg DEBUG_BUILD=n
	# Package
	tar cvzf prebuilt/reglinux-mame-${MAME_VERSION}-${arch}.tar.gz output/${arch}/per-package/mame/target/usr/bin/mame/ output/${arch}/per-package/libretro-mame/target/usr/lib/libretro/mame_libretro.so output/${arch}/per-package/mame/target/usr/share/mame/ output/${arch}/per-package/libretro-mame/target/usr/share/lr-mame/
	# Clean again
	make ${arch}-clean
done

# Disable the flag to build MAME from source
sed -i s/BR2_PACKAGE_MAME_BUILD_FROM_SOURCE=y/#BR2_PACKAGE_MAME_BUILD_FROM_SOURCE=y/ configs/reglinux-board.common

