# C-Dogs SDL

The REG-Linux `cdogs-sdl` port delivers the classic overhead run-and-gun engine with Python/ENet helpers so multiplayer maps target the distro.

## Build notes

- `Version`: 2.3.2 (Aug 2025) release with the upstream CMake tree.
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_MIXER`, `BR2_PACKAGE_PYTHON`, `BR2_PACKAGE_PYTHON_PROTOBUF`, `BR2_PACKAGE_ENET`, `BR2_INSTALL_LIBSTDCPP`.
- `Build helper`: CMake-based (`cmake-package`) with `CDOGS_SUPPORTS_IN_SOURCE_BUILD=NO`, disabled editor/tests, and shared ENet.
- `Extras`: targets `/userdata/roms/cdogs` for assets, copies `cdogs.keys` into `/usr/share/evmapy`, and relies on the content downloader to supply the data pack.
