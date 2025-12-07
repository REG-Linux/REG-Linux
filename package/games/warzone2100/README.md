# Warzone 2100

Free, open-source 3D RTS with campaign, skirmish, and multiplayer modes.

## Build notes
- **Version:** 4.6.1 release (Sept 2025) with source tarball from GitHub.
- **Config:** selects SDL2, libsodium, SQLite (+ column metadata), protobuf, libzip, PhysFS, OpenAL, libtheora, libcurl, and requires a C++ toolchain.
- **Build system:** CMake release build with `WARZONE2100_SUPPORTS_IN_SOURCE_BUILD = NO` and no extra install hooks beyond the default.
- **Notes:** uses typical CMake packaging so the resulting binary is available in `/usr/bin` with all standard assets delivered by the upstream source.
