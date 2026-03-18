# ioquake3

Quake III Arena engine community continuation. Upstream: https://github.com/ioquake/ioq3

Installs under `/usr/ioquake3/`. On RISC-V, `-mno-relax` is added to work around a GCC 15 LTO bug. `USE_INTERNAL_LIBS=OFF` forces use of the sysroot-provided libraries.
