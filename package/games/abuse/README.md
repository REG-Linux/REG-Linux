# Abuse

REG-Linux builds the Xenoveritas SDL port of *Abuse*, keeping the asset dir pointed at `/userdata/roms/abuse` so the distro’s content downloader can supply the data separately.

## Build notes

- `Version`: `v0.9.1` (Oct 27, 2022 commit) from the `abuse` SDL tree.
- `Dependencies`: `BR2_PACKAGE_SDL2`, `BR2_PACKAGE_SDL2_MIXER`, `BR2_INSTALL_LIBSTDCPP`.
- `Build helper`: CMake-based (`cmake-package`) with `ABUSE_SUPPORTS_IN_SOURCE_BUILD=NO` and `-DASSETDIR` pointing at `/userdata/roms/abuse`.
- `Extras`: installs `abuse.keys` into `/usr/share/evmapy` and leaves the game data to the `package/games/abuse-data` pack or an external downloader.
