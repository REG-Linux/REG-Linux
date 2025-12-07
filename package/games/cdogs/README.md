# C-Dogs SDL

Classic overhead run-and-gun game compiled from the `cdogs-sdl` source tree.

## Build notes
- **Version:** 2.3.2 release (Aug 2025).
- **Config:** selects SDL2, SDL2_mixer, Python protobuf on both host and target, ENet, and requires a C++ toolchain.
- **Build system:** CMake release build with `CDOGS_SUPPORTS_IN_SOURCE_BUILD = NO`, hard-coded data directory (`/userdata/roms/cdogs`), the editor/test suite disabled, and shared ENet enabled. A pre-configure hook strips the tests directory.
- **Install:** installs the binary, leaves asset management to the content downloader (the commented-out copy steps document where doc/data/graphics lived), and copies `cdogs.keys` into `/usr/share/evmapy` for controller mapping.
