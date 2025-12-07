# OpenBOR 6412

`openbor6412` packages release `05af203b0e5676034678291bbedc0b9fe4c8f898` of the `DCurrent/openbor` engine with extra compatibility fixes.

## Configuration
- **Config selection:** selects `libvpx`, `SDL2`, `SDL2_gfx`, `libpng`, `libogg`, and `libvorbis`.
- **Build flow:** similar to other branches, runs `engine/version.sh`, then invokes `make` with the target-specific `BUILD_*` flags, and installs `OpenBOR6412` under `/usr/bin`.

## Included patches
- `0001-Fix-anim_list-and-model_cache-definitions.patch`
- `001-x86_64.patch`
- `002-fixkeys.patch`
- `003-arm.patch`
- `004-warnings.patch`
- `005-axismanagement.patch`
- `006-fix-pad-axis-combos-player-running.patch`
- `100-openbor-c.patch`
- `100-openbor-h.patch`
- `101-openbor-c-savedata-fullscreen.patch`
- `101-openbor-h.patch`
