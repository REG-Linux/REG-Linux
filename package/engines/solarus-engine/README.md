# Solarus engine

Solarus is a Lua-scripted Zelda-like engine built with CMake and LuaJIT for REG-Linux.

## Configuration
- **Version:** v2.0.2 (December 2025 release).
- **Config selections:** requires `reglinux-luajit`, OpenAL, GL/GLES, libmodplug, libogg, libvorbis, PhysFS, SDL2 (+image/ttf), GLM, and `BR2_TOOLCHAIN` features for threads/NPTL.
- **Build options:** disables the Qt-based GUI, sets custom write directories, forces LuaJIT, and enables GLES when available.

## Patches
- `001-cmake-remove-Werror.patch` removes `-Werror` for Buildroot builds.
- `002-pad.patch` and `003-padnum.patch` fix controller mapping and pad numbering issues.
