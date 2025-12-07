# OpenBOR 7142

`openbor7142` packages commit `3caaddd5545ea916aaeef329ba43c9f2c4a451cc` from `DCurrent/openbor` with wide-ranging controller and display tweaks.

## Configuration
- **Config selection:** selects `libvpx`, `SDL2`, `SDL2_gfx`, `libpng`, `libogg`, and `libvorbis`.
- **Build flow:** runs `engine/version.sh` and builds via `make`, injecting `BUILD_LINUX`/`BUILD_ARM`/`BUILD_MIPSEL` based on the target. The `OpenBOR7142` binary installs under `/usr/bin`.

## Included patches
- `001-x86_64.patch`
- `002-parsableconfigkeys.patch`
- `003-arm.patch`
- `004-warnings.patch`
- `006-fix-pad-axis-combos-player-running.patch`
- `007-version.patch`
- `008-vsync.patch`
- `009-sdlpads.patch`
- `010-sdlaxespads.patch`
- `defaults-fullscreen.patch`
