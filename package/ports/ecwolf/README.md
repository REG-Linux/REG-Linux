# ECWolf (Wolfenstein 3D)

Port of Wolfenstein 3D built on ECWolf (Wolf4SDL derivative) that reuses host-generated executables.

## Build notes
- **Version:** 1.5pre, built from the Bitbucket git tree with CMake.
- **Config:** picks up SDL2, SDL2_net/mixer, zlib, bzip2, JPEG, and optionally FluidSynth plus the musl helpers; it also builds a `host-ecwolf` toolchain package to generate the `ImportExecutables.cmake` snippet ECWolf consumes.
- **Build system:** CMake release build with `ImportExecutables.cmake` injection, cross-compilation flags, and header-copying hooks to satisfy `gdtoa`.
- **Extras:** installs the `ecwolf` binary under `/usr/share/ecwolf` and symlinks `/usr/bin/ecwolf`; copies `ecwolf.keys` to `/usr/share/evmapy`.
