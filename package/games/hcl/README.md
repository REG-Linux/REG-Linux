# Hydra Castle Labyrinth

`hydracastlelabyrinth` brings the retro-inspired platformer to REG-Linux using SDL2/SDL2_mixer plus the distro’s pad helpers.

## Build notes

- `Version`: `229369c...` (Feb 2024) commit from `ptitSeb/hydracastlelabyrinth`.
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_MIXER`, `BR2_INSTALL_LIBSTDCPP`.
- `Build helper`: CMake-based (`cmake-package`) with `USE_SDL2=ON` and Buildroot patches for the CMake build/pad handling (`001-cmake.patch`, `002-sdl2_pad.patch`).
- `Extras`: installs the `hcl` binary into `/usr/bin` and copies `hcl.keys` into `/usr/share/evmapy`.
