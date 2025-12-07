# OpenBOR packages

The `openbor` folder holds multiple OpenBOR builds derived from DCurrent's forks. Each subdirectory is an independent Buildroot recipe that compiles a specific engine revision, applies device-specific patches, and installs the `OpenBOR` binary under `/usr/bin`.

## Available revisions
- `openbor4432`: early `v3b4432` release with GCC option and pad fixes.
- `openbor6330`, `openbor6412`, `openbor6510`: later branches with axis/pad tweaks plus `openbor-c`/`openbor-h` fixes and warning cleanups.
- `openbor7142`: modern fork with fullscreen defaults, SDL/Gamepad patches, and vsync tweaks.
- `openbor7530`: OpenBOR 4.x (`v7533`) build with updated makefiles, path adjustments, and hotkey exit handling.

Each package selects `libvpx`, `SDL2`, `SDL2_gfx`, `libpng`, `libogg`, and `libvorbis`. The Makefiles detect the target (x86_64, ARM, MIPS, RISC-V) and pass appropriate `BUILD_*` flags via `MAKE`. Refer to the README inside each revision for precise patch lists and version-specific notes.
