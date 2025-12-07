# Libretro cores for REG-Linux

This folder keeps the libretro builds that integrate with our emulator front-ends. Each subdirectory defines a standalone Buildroot package producing a single `.so` core.

## libretro-easyrpg
- Builds the EasyRPG Player as a libretro core (v0.8.1.1).
- Selects SDL2, SDL2_mixer, libpng, zlib, fmt, freetype, mpg123, libvorbis, opusfile, pixman, speexdsp, libxmp, wildmidi, liblcf, json-for-modern-cpp, libsndfile, and lhasa so the core can load RPG Maker games.
- CMake-based (`cmake-package`) build with shared/static libs enabled; installs `easyrpg_libretro.so` under `/usr/lib/libretro`.

## libretro-scummvm
- Wraps ScummVM (v2.9.1) into a libretro platform build, cloning `libretro-common` and `libretro-deps` with pinned commits.
- Configures GLES or desktop GL depending on the target and forces GLES2 by default; adds NEON/SSE flags per architecture and switches between Tremor/Vorbis.
- Builds the core at `backends/platform/libretro` and installs `scummvm_libretro.so`.
