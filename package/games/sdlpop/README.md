# SDLPoP

Prince of Persia port built from the disassembly project.

## Build notes
- **Version:** `v1.24-RC` (April 2025) using the `SDLPoP` repository with `src` as the build directory.
- **Config:** selects SDL2 and SDL2_image, requires a C++ toolchain.
- **Build system:** CMake release build; installs the `prince` binary as `/usr/bin/SDLPoP`, copies the `SDLPoP.ini` configuration, and creates an empty `SDLPoP.cfg` for advanced tweaks.
- **Install extras:** copies the `data/` directory from the repo and registers `sdlpop.keys` in `/usr/share/evmapy`.
