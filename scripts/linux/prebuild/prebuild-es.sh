#!/bin/sh

# Run this script from root directory of the project like
# ./scripts/linux/prebuild-es.sh


echo "Building REG-ES generic build for all archs"

REG_ES_VERSION="test"

# Create prebuilt output directory
mkdir -p prebuilt

# Loop over archs (armhf armv7 aarch64 x86_64 riscv64gc)
for arch in bcm2835 bcm2836 h5 x86_64 jh7110; do
	# Clean
	make ${arch}-clean
	# Build
	PKG=reglinux-emulationstation make ${arch}-pkg PARALLEL_BUILD=1
	# Package
	tar cvzf prebuilt/reglinux-es-${REG_ES_VERSION}-${arch}.tar.gz output/${arch}/per-package/reglinux-emulationstation/target/usr/bin/emulationstation
	# Clean again
	make ${arch}-clean
done

