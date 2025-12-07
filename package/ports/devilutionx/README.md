# DevilutionX (Diablo I)

Builds the modern Diablo I source port with libpng and SDL2 tooling.

## Build notes
- **Version:** 1.5.5 release, downloaded as a tarball.
- **Config:** selects `SDL2`, `SDL2_image`, `Fmt`, `libsodium`, `Bzip2` plus the standard codec stack.
- **Build system:** release CMake that enables static libs, disables tests, pre-fills a player name, and forbids FetchContent to ensure offline builds.
- **Extras:** registers `devilutionx.keys` in `/usr/share/evmapy`.
