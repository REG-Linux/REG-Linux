# OpenBOR 6510

`openbor6510` builds the `v6510-dev` branch while reusing the SDL2 and codec stack used elsewhere in the `openbor` folder.

## Configuration
- **Config selection:** selects `libvpx`, `SDL2`, `SDL2_gfx`, `libpng`, `libogg`, and `libvorbis`.
- **Build flow:** runs `engine/version.sh`, then `make` with architecture-aware `BUILD_*` options before installing `OpenBOR6510` under `/usr/bin`.

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
