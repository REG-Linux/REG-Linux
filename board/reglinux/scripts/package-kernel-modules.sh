#!/bin/bash

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

# Remove previous modules file if present
if [ -f  "${BINARIES_DIR}/modules" ]; then
	rm "${BINARIES_DIR}/modules"
fi

# Determine squashfs compression from buildroot config (default: zstd)
# Match buildroot's own flags (e.g. lz4 needs -Xhc for old kernel compat)
MODULES_COMP="zstd"
MODULES_COMP_EXTRA=""
if [ -n "${BR2_CONFIG}" ] && [ -f "${BR2_CONFIG}" ]; then
	COMP_FROM_CONFIG=$(sed -n 's/^BR2_TARGET_ROOTFS_SQUASHFS4_\([A-Z0-9]*\)=y$/\1/p' "${BR2_CONFIG}" | tr 'A-Z' 'a-z')
	if [ -n "${COMP_FROM_CONFIG}" ]; then
		MODULES_COMP="${COMP_FROM_CONFIG}"
		# lz4 high-compression mode for kernel compatibility (matches squashfs.mk)
		if [ "${MODULES_COMP}" = "lz4" ]; then
			MODULES_COMP_EXTRA="-Xhc"
		fi
	fi
fi

# Package new one
rm -rf /tmp/modules-squashfs
mkdir -p /tmp/modules-squashfs/lib
cp -a "${TARGET_DIR}/lib/modules" /tmp/modules-squashfs/lib/
"${HOST_DIR}/bin/mksquashfs" "/tmp/modules-squashfs" "${BINARIES_DIR}/modules" -comp ${MODULES_COMP} ${MODULES_COMP_EXTRA}
rm -rf /tmp/modules-squashfs
