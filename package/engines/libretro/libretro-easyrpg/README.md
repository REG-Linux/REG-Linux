# libretro-easyrpg core

Wraps EasyRPG Player as a libretro core for frontend display.

## Build details
- **Version:** 0.8.1.1 from `EasyRPG/Player` with git submodules.
- **Config:** selects the full SDL2 stack plus libpng, fmt, freetype, mpg123, libvorbis, opusfile, pixman, speexdsp, libxmp, wildmidi, liblcf, json-for-modern-cpp, libsndfile, and lhasa to satisfy the player components; optional `harfbuzz` and `fluidsynth` follow their Buildroot equivalents.
- **Build system:** CMake (`cmake-package`) with release build, forces shared/static builds, and sets `-fPIC` flags. The resulting `easyrpg_libretro.so` installs under `/usr/lib/libretro`.
