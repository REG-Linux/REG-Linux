# OpenRCT2 (RollerCoaster Tycoon 2 engine)

Open-source reimplementation of RollerCoaster Tycoon 2.

## Build notes
- **Version:** v0.4.26 (Sept 2025).
- **Config:** selects SDL2, libcurl, libzip, speexdsp, FLAC, libvorbis, and json-for-modern-cpp, plus C++ toolchain support (`BR2_INSTALL_LIBSTDCPP`).
- **Build system:** CMake release build that enforces static libs, disables Discord RPC, and conditionally disables OpenGL when none is available. Out-of-tree build is enforced.
- **Extras:** no host tools yet, but the recipe leaves commented host build scaffolding for future use.
