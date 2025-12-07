# OpenBOR 7530 (OpenBOR 4)

`openbor7530` builds the OpenBOR 4.x branch (`v7533`) maintained by DCurrent, which is the most modern release in the repository.

## Configuration
- **Config selection:** selects `libvpx`, `SDL2`, `SDL2_gfx`, `libpng`, `libogg`, and `libvorbis`.
- **Build flow:** prepares the version string using `version.sh` (updates the `VERSION_BUILD` variable) and calls `make` with `BUILD_LINUX_LE_x86_64`, `BUILD_LINUX`, or `BUILD_LINUX_LE_arm` depending on the architecture. The packaged binary is installed as `/usr/bin/OpenBOR7530`.

## Included patches
- `001-fix-makefile.patch`
- `002-adjust-paths.patch`
- `003-version.patch`
- `004-parsable-config-keys.patch`
- `005-hotkey-exit.patch`
