# Hydra Castle Labyrinth

Platformer inspired by 16-bit era games.

## Build notes
- **Version:** commit `229369c...` (Feb 2024) from `ptitSeb/hydracastlelabyrinth`.
- **Config:** selects SDL2 and SDL2_mixer and depends on a C++ toolchain.
- **Build system:** CMake release build with `USE_SDL2=ON`, a couple of Buildroot patches for the CMake flow and pad handling (`001-cmake.patch`, `002-sdl2_pad.patch`).
- **Install:** copies the `hcl` binary to `/usr/bin` and installs `hcl.keys` under `/usr/share/evmapy`.
