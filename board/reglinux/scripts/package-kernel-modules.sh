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

# Package new one
"${HOST_DIR}/bin/mksquashfs" "${TARGET_DIR}/lib/modules/" "${BINARIES_DIR}/modules" -comp zstd
