#!/bin/sh

# Run this script from root directory of the project like
# ./scripts/linux/prebuild-scummvms.sh

# Grab ScummVM version from source tree
SCUMMVM_VERSION=$(cat package/engines/scummvm/scummvm.mk | grep SCUMMVM_VERSION | cut -d "=" -f 2 | head -n1 | tr -d '[:space:]')
LRSCUMMVM_VERSION=$(cat package/engines/libretro/libretro-scummvm/libretro-scummvm.mk | grep LIBRETRO_SCUMMVM_VERSION | cut -d "=" -f 2 | head -n1 | tr -d '[:space:]')

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
sed -i s/#BR2_PACKAGE_SCUMMVM_BUILD_FROM_SOURCE=y/BR2_PACKAGE_SCUMMVM_BUILD_FROM_SOURCE=y/ configs/reglinux-board.common

# Loop over 32-bit archs / musl libc
# bcm2836 can be used for h3/cha and rk3128 (cortex_a7)
for arch in jz4770 bcm2835 bcm2836 s812 odroidxu4 rk3288; do
	# Clean
	make ${arch}-clean
	# Build
	PKG=scummvm make ${arch}-pkg DEBUG_BUILD=n
	PKG=libretro-scummvm make ${arch}-pkg DEBUG_BUILD=n
	# Package
	tar --transform='s|[^/]*/[^/]*/[^/]*/[^/]*/[^/]*/||' -cvzf prebuilt/reglinux-scummvm-${SCUMMVM_VERSION}-${arch}.tar.gz output/${arch}/per-package/scummvm/target/usr/bin/scummvm output/${arch}/per-package/libretro-scummvm/target/usr/lib/libretro/scummvm_libretro.so output/${arch}/per-package/scummvm/target/usr/share/scummvm output/${arch}/per-package/scummvm/target/usr/lib/scummvm
	# Clean again
	make ${arch}-clean
done
# Loop over 64-bit archs (except x86)
# rk3326 is cortex_a35/musl
# s9gen4 is cortex_a35/glibc
# h5 can be used for h6, h616, h700, s905, s905gen2, rk3328 (cortex_a53/musl)
# s905gen3 can be used for rk3566/rk3568 (cortex_a55/glibc)
# s922x can be used for a3gen2 (cortex_a73_a53/glibc)
# rk3588 can be used for sm8250 (cortex_a76_a55)
# sm8550 is ARMv9 / glibc
for arch in h5 bcm2711 bcm2712 rk3326 rk3399 rk3588 s905gen3 s922x s9gen4 sm8550 asahi jh7110 k1; do
	# Clean
	make ${arch}-clean
	# Build
	PKG=scummvm make ${arch}-pkg DEBUG_BUILD=n
	PKG=libretro-scummvm make ${arch}-pkg DEBUG_BUILD=n
	# Package
	tar --transform='s|[^/]*/[^/]*/[^/]*/[^/]*/[^/]*/||' -cvzf prebuilt/reglinux-scummvm-${SCUMMVM_VERSION}-${arch}.tar.gz output/${arch}/per-package/scummvm/target/usr/bin/scummvm output/${arch}/per-package/libretro-scummvm/target/usr/lib/libretro/scummvm_libretro.so output/${arch}/per-package/scummvm/target/usr/share/scummvm output/${arch}/per-package/scummvm/target/usr/lib/scummvm
	# Clean again
	make ${arch}-clean
done
# x86_64 variants are monolithic builds (no plugins, so no $(TARGET_DIR)/usr/lib/scummvm folder
for arch in x86_64 x86_64_v3; do
	# Clean
	make ${arch}-clean
	# Build
	PKG=scummvm make ${arch}-pkg DEBUG_BUILD=n
	PKG=libretro-scummvm make ${arch}-pkg DEBUG_BUILD=n
	# Package
	tar --transform='s|[^/]*/[^/]*/[^/]*/[^/]*/[^/]*/||' -cvzf prebuilt/reglinux-scummvm-${SCUMMVM_VERSION}-${arch}.tar.gz output/${arch}/per-package/scummvm/target/usr/bin/scummvm output/${arch}/per-package/libretro-scummvm/target/usr/lib/libretro/scummvm_libretro.so output/${arch}/per-package/scummvm/target/usr/share/scummvm
	# Clean again
	make ${arch}-clean
done

# Disable the flag to build ScummVM from source
sed -i s/BR2_PACKAGE_SCUMMVM_BUILD_FROM_SOURCE=y/#BR2_PACKAGE_SCUMMVM_BUILD_FROM_SOURCE=y/ configs/reglinux-board.common

