# ioquake3

Quake III Arena engine community continuation. Upstream: https://github.com/ioquake/ioq3

Installs via the `datainit` tree, so the binary, renderer plugins, and per-mod cgame/qagame/ui modules land directly in `/userdata/roms/quake3` on first boot (see `board/fsoverlay/etc/init.d/S12populateshare`); `/usr/bin/ioquake3` is a symlink into that eventual location so regmsgd's launcher resolver can detect the emulator. On RISC-V, `-mno-relax` is added to work around a GCC 15 LTO bug. `USE_INTERNAL_LIBS=OFF` forces use of the sysroot-provided libraries.
