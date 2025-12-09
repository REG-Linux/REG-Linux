# SDLPoP

SDLPoP ports the Prince of Persia disassembly build to REG-Linux, bundling the upstream data directories and config scaffolding for embedded targets.

## Build notes

- `Version`: `v1.24-RC` (Apr 2025) release from the `SDLPoP` repo.
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_IMAGE`, `BR2_INSTALL_LIBSTDCPP`.
- `Build helper`: CMake-based (`cmake-package`) with the `src` directory as the build root.
- `Extras`: installs `/usr/bin/SDLPoP`, copies the `data/` directory plus `SDLPoP.ini`, creates `SDLPoP.cfg`, and copies `sdlpop.keys` into `/usr/share/evmapy`.
