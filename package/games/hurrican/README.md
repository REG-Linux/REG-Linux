# Hurrican

SDL2-enabled fork of the freeware shooter/platformer with OpenGL abstraction tweaks.

## Build notes
- **Version:** commit `16205675479d49f...` (Nov 2025) from `HurricanGame/Hurrican`.
- **Config:** selects SDL2, SDL2_mixer, SDL2_image, libepoxy, libopenmpt, and requires a C++ toolchain.
- **Build system:** CMake release build that enables GLES2 rendering (`-DRENDERER=GLES2`), applies custom `001-paths.patch` to fix install paths, and copies the resulting `hurrican` binary to `/usr/bin`.
- **Install:** ensures `/usr/share/hurrican` exists, installs the executable, and copies `hurrican.keys` into `/usr/share/evmapy` for controller mapping.
