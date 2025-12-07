# libretro-scummvm core

Builds the ScummVM project as a libretro core using the `backends/platform/libretro` subsystem.

## Build details
- **Version:** v2.9.1 branch from the ScummVM repository.
- **Config:** depends on C++ toolchain plus `BR2_PACKAGE_HAS_LIBRETRO_SCUMMVM` (selected by downstream packages). Mirrors the full codec stack selected for the standalone ScummVM build (SDL2, libogg/vorbis or Tremor, libmad, libmpeg2, etc.).
- **Build flow:** clones `libretro-deps` and `libretro-common` via helper macros, configures host/target flags based on the target architecture, and forces GLES2 unless the target provides desktop GL support. Builds `scummvm_libretro.so` and installs it into `/usr/lib/libretro`.
