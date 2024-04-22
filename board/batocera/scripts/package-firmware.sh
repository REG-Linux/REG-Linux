#!/bin/bash

# PWD = source dir
# BASE_DIR = build dir
# BUILD_DIR = base dir/build
# HOST_DIR = base dir/host
# BINARIES_DIR = images dir
# TARGET_DIR = target dir

# Remove previous firmware file if present
if [ -f  "${BINARIES_DIR}/firmware" ]; then
	rm "${BINARIES_DIR}/firmware"
fi

# Package new one
"${HOST_DIR}/bin/mksquashfs" "${TARGET_DIR}/lib/firmware/" "${BINARIES_DIR}/firmware" -comp xz
